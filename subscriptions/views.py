from django.shortcuts import render
from django.views.decorators.http import require_POST
from .forms import NewUserForm, LoginForm
from .models import NewUser

import myproject.settings as settings
import stripe
import json
from djstripe.models import Product, PaymentMethod, Customer, Subscription
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def home(request):
    # Renders login Page
    return render(request, "login.html", {"form": LoginForm()})


@require_POST
def new_customer(request):
    body = json.loads(request.body)
    # Retrieve payment method from Stripe data
    payment_method = stripe.PaymentMethod.retrieve(body['payment_method'])
    PaymentMethod.sync_from_stripe_data(payment_method)
    user = NewUser.objects.get(username=body['user'])
    if not getattr(user, 'owner'):
        # If customer doesn't exist, create new Customer object
        customer = stripe.Customer.create(email=getattr(user, 'email'),
                                          payment_method=payment_method,
                                          invoice_settings={"default_payment_method": payment_method}, )
    else:
        # Attach new payment method to customer
        customer = stripe.Customer.retrieve(getattr(user, 'owner').id)
        stripe.PaymentMethod.attach(payment_method, customer=customer.id)
        stripe.Customer.modify(
            customer.id,
            invoice_settings={"default_payment_method": payment_method},
        )

    # Create new Subscription and attach to customer
    subscription = stripe.Subscription.create(customer=customer.id,
                                              items=[{'price': body['price_id']}],
                                              expand=['latest_invoice.payment_intent'],
                                              trial_period_days=7)

    # Save in Django DB
    django_customer = Customer.sync_from_stripe_data(customer)
    user.owner = django_customer
    django_subscription = Subscription.sync_from_stripe_data(subscription)
    user.subscription = django_subscription
    user.save()
    return JsonResponse(data={
        'customer': customer,
        'subscription': subscription
    })


@require_POST
def retry_subscription(request):
    body = json.loads(request.body)
    # Attach new Payment method to Customer
    stripe.PaymentMethod.attach(body['payment_method'], customer=body['customer_id'])
    stripe.Customer.modify(body['customer_id'], invoice_settings={'default_payment_method': body['payment_method']})
    return JsonResponse(data={
        'invoice': stripe.Invoice.retrieve(body['invoice'], expand=['payment_intent'])
    })


def create_subscription(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            # Save user data in Django DB
            user = form.cleaned_data['username']
            form.save()
            # Create new session to log user in
            request.session['username'] = user
            # Redirect user to register for a plan
            return render(request, "plan_signup.html", {"product": Product.objects.get(name="WhatsBusy Premium"),
                                                        "person": NewUser.objects.get(username=user),
                                                        "key": settings.STRIPE_TEST_PUBLIC_KEY})
        else:
            # Registration info incorrect/invalid
            return render(request, "registration_disallowed.html", {})
    elif 'username' in request.session:
        # If user is already logged in, simply redirect to payment page
        return render(request, "plan_signup.html", {"product": Product.objects.get(name="WhatsBusy Premium"),
                                                    "person": request.session['username'],
                                                    "key": settings.STRIPE_TEST_PUBLIC_KEY})


@require_POST
def cancel_subscription(request):
    body = json.loads(request.body)
    user = NewUser.objects.get(username=body['user'])
    sub_id = user.subscription.id
    # Delete subscription and sync from Stripe to Django DB
    cancelled_subscription = stripe.Subscription.delete(sub_id)
    user.subscription = Subscription.sync_from_stripe_data(cancelled_subscription)
    return JsonResponse(data={
        'cancelledSubscription': cancelled_subscription,
    })


def logout(request):
    # Remove session and render login page
    try:
        del request.session['username']
    except Exception:
        pass
    return render(request, "login.html", {"form": LoginForm()})


def main_page(request, user):
    if request.method == 'POST':
        user_info = LoginForm(request.POST)
        if user_info.is_valid():
            # If login information is correct, create session and redirect to user's homepage
            username = user_info.cleaned_data['username']
            request.session['username'] = username
            return render(request, 'homepage.html', {"user": NewUser.objects.get(username=username)})
    elif 'username' in request.session and request.session['username'] == user:
        # If navigating from another page besides the login page and session exists, return homepage
        return render(request, 'homepage.html', {"user": NewUser.objects.get(username=user)})
    else:
        # Show Login Page if no user is logged in
        return render(request, 'login.html', {"form": LoginForm()})

"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.urls import include, path
from django_registration.backends.one_step.views import RegistrationView
from subscriptions import views, forms

urlpatterns = [
    path('new-customer/', views.new_customer, name="new_customer"),
    path('retry-subscription/', views.retry_subscription, name="retry_subscription"),
    path('cancel-subscription/', views.cancel_subscription),
    path('accounts/register/', RegistrationView.as_view(form_class=forms.NewUserForm),
         name="django_registration_register"),
    path('activate-trial/', views.create_subscription, name="create_subscription"),
    path('accounts/loggedin/<str:user>', views.main_page, name="main_page"),
    path('logout/', views.logout, name="logout"),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    url(r'^$', views.home, name='home'),
]

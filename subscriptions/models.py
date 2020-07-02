from django.db import models
from django.contrib.auth.models import AbstractUser


# Model for users in DB, contains same fields as AbstractUser but adds a field for a DJ-Stripe Customer
# and a DJ-Stripe Subscription
class NewUser(AbstractUser):
    owner = models.ForeignKey('djstripe.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    subscription = models.ForeignKey('djstripe.Subscription', on_delete=models.SET_NULL, null=True, blank=True)

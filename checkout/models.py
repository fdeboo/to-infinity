"""
Billing store information related to the payment aspect of the booking
"""

from django.db import models
from django_countries.fields import CountryField
from bookings.models import Booking


class Billing(models.Model):
    """ Stores the user's billing address """

    country = CountryField(blank_label="Country *", null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    original_bag = models.TextField(null=False, blank=False, default="")
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default=""
    )
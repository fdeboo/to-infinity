"""
Models include Order and Order Line Item
"""
from django.db import models
from django.db.models import Sum
from django_countries.fields import CountryField
from bookings.models import Booking


class Billing(models.Model):

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label="Country *", null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    original_bag = models.TextField(null=False, blank=False, default="")
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default=""
    )

    def update_total(self):
        """
        Update booking total each time a line item is added
        """

        self.order_total = self.bookingitems.aggregate(Sum("line_total"))[
            "line_total__sum"
        ]
        self.save()
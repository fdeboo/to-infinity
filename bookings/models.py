"""
Models include Trip, Passenger and Booking Line Item
"""
import uuid
from django.db import models
from django.db.models import Count
from products.models import Destination, Product


class Trip(models.Model):
    """
    Stores information about each Trip on offer to any given destination
    Monitors how many seats are left available as booking are made

    """
    destination = models.ForeignKey(
        Destination,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="trips",
    )
    date = models.DateTimeField()
    seats_available = models.IntegerField(
        null=False, blank=False, editable=False
    )

    def save(self, *args, **kwargs):
        """
        Override the original save method and update the number of
        seats available
        """
        reservations = (
            Booking.objects.aggregate(
                num_passengers=Count("passengers")
            )
            ["num_passengers"] or 0
        )
        self.seats_available = self.destination.max_passengers - reservations
        super().save(*args, **kwargs)

    def __str__(self):
        date = (self.date).strftime("%A %d %B %Y")
        return date


class Booking(models.Model):
    """ Model stores information about each booking such as which trip
    the booking is for, details of the passengers and the overall cost  """

    booking_ref = models.CharField(
        primary_key=True, max_length=20, null=False, editable=False
    )
    trip = models.ForeignKey(
        Trip, on_delete=models.SET_NULL, null=True, blank=False
    )
    """
    lead_user = models.ForeignKey(
        "UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    """
    booking_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default=""
    )
    num_passengers = models.IntegerField(null=False, blank=False)

    def _generate_booking_ref(self):
        """ Generate a random, unique order number using UUID """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the booking reference
        if it hasn't been set already
        """

        if not self.booking_ref:
            self.booking_ref = self._generate_booking_ref()
        super().save(*args, **kwargs)


class Passenger(models.Model):
    """ Store information about each passenger included
    in a booking """

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="passengers"
    )
    first_name = models.CharField(max_length=20, null=False, blank=False)
    last_name = models.CharField(max_length=20, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    is_leaduser = models.BooleanField(null=False, blank=False, default=False)
    """"
    medical_assessment = models.OneToOneField(
        "Medical",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    """


class BookingLineItem(models.Model):
    """
    Related to the products being sold as part of the booking.
    Each instance is an individual product that make up the order.
    Calculates the total based on the quantity applied.
    """

    booking = models.ForeignKey(
        Booking,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="lineitems",
    )
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE
    )
    quantity = models.IntegerField(null=False, blank=False, default=0)
    line_total = models.DecimalField(
        max_digits=8, decimal_places=2, null=False, blank=False, editable=False
    )

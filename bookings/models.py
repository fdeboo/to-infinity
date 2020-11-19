import uuid
from django.db import models
from django.db.models import Count
from products.models import Destination, Product


class Trip(models.Model):
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
        Override the original save method and set the number of
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


class Booking(models.Model):
    booking_ref = models.CharField(
        primary_key=True, max_length=20, null=False, editable=False
    )
    trip = models.ForeignKey(
        Trip, on_delete=models.SET_NULL, null=True, blank=False
    )
    """
    user_profile = models.ForeignKey(
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
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    num_passengers = models.IntegerField(null=False, blank=False)

    def _generate_booking_ref(self):
        """
        Generate a random, unique order number using UUID
        """
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
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="passengers"
    )
    first_name = models.CharField(max_length=20, null=False, blank=False)
    last_name = models.CharField(max_length=20, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    """"
    medical_assessment = models.OneToOneField(
        "Medical",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    """


class BookingLineItem(models.Model):
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

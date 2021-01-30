"""
Models include Trip, Passenger and Booking Line Item
"""
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.db.models import Count, Sum
from products.models import Destination, Product, AddOn, Insurance
from profiles.models import UserProfile


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
    trip_ref = models.CharField(
        max_length=32, null=True, editable=True, blank=True
    )

    def update_seats_available(self):
        """
        Override the original save method and update the number of
        seats available
        """
        reservations = self.bookings.filter(status="COMPLETE").aggregate(
            num_passengers=Count("passengers")
        )["num_passengers"]
        self.save(reservations=reservations)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the trip reference and
        seats_available if not set already
        """

        if not self.trip_ref:
            date = (self.date).strftime("%m%d-%y")
            self.trip_ref = self.destination.pk + "-" + date

        reservations = kwargs.pop("reservations", 0)
        self.seats_available = self.destination.max_passengers - reservations
        super().save(*args, **kwargs)

    def __str__(self):
        date = (self.date).strftime("%d/%m/%Y")
        return f"{self.destination} on {date}"

    class Meta:
        ordering = ["date"]


class Booking(models.Model):
    """Model stores information about each booking such as which trip
    the booking is for, details of the passengers and the overall cost"""

    BOOKING_STATUS_CHOICES = [
        ("OPENED", "Open"),
        ("COMPLETE", "Complete"),
        ("CANCELLED", "Cancelled"),
    ]
    booking_ref = models.CharField(
        primary_key=True, max_length=32, null=False, editable=False
        )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="bookings",
    )
    lead_user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    booking_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    status = models.CharField(
        max_length=10, null=False,
        blank=False,
        choices=BOOKING_STATUS_CHOICES,
        default="OPENED",
    )
    full_name = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    contact_email = models.EmailField(max_length=50, null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True, editable=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    original_bag = models.TextField(null=False, blank=False, default="")
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default=""
    )

    def _generate_booking_ref(self):
        """ Generate a random, unique order number using UUID """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update booking total each time a line item is added
        """

        self.booking_total = self.bookingitems.aggregate(Sum("line_total"))[
            "line_total__sum"
        ]
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the booking reference
        if it hasn't been set already
        """

        if not self.booking_ref:
            self.date_created = timezone.now()
            self.booking_ref = self._generate_booking_ref()
        super().save(*args, **kwargs)


class Passenger(models.Model):
    """Store information about each passenger included
    in a booking"""

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="passengers"
    )
    first_name = models.CharField(max_length=20, null=False, blank=False)
    last_name = models.CharField(max_length=20, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    passport_no = models.CharField(
        max_length=9,
        null=False,
        blank=False,
        validators=[MinLengthValidator(9, message="Does not meet the required \
            length")]
    )
    is_leadpassenger = models.BooleanField(
        null=False, blank=False, default=False, editable=False)
    trip_addons = models.ManyToManyField(AddOn, blank=True)
    trip_insurance = models.ManyToManyField(Insurance)
    """"
    medical_assessment = models.OneToOneField(
        "Medical",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    """

    @property
    def full_name(self):
        """ Combines the first and last name of the passenger """

        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class BookingLineItem(models.Model):
    """
    Related to the products being sold as part of the booking.
    Each instance is an individual product that makes up the order.
    Calculates the total based on the quantity applied.
    """

    booking = models.ForeignKey(
        Booking,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="bookingitems",
    )
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE
    )
    quantity = models.IntegerField(null=False, blank=False, default=0)
    line_total = models.DecimalField(
        max_digits=8, decimal_places=2, null=False, blank=False, editable=False
    )

    def save(self, *args, **kwargs):
        """
        Overrides the original save method to set the line total
        and update the order total
        """
        self.line_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product.name

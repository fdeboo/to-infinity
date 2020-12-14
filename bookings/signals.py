""" Receives a signal whenever the BookingLineIem is saved """
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import BookingLineItem, Passenger, Booking


@receiver(post_save, sender=BookingLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update booking total on lineitem update/create
    """
    instance.booking.update_total()


@receiver(post_save, sender=Passenger)
def update_seats_available_on_save(sender, instance, created, **kwargs):
    """
    Update number of passengers on passengers update/create
    """
    instance.booking.trip.update_seats_available()


@receiver(post_delete, sender=Booking)
def update_seats_available_on_save(sender, instance, created, **kwargs):
    """
    Update number of passengers on passengers update/create
    """
    instance.booking.trip.update_seats_available()
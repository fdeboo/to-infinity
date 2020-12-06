""" Receives a signal whenever the BookingLineIem is saved """
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BookingLineItem


@receiver(post_save, sender=BookingLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update booking total on lineitem update/create
    """
    print("postsaved")
    instance.booking.update_total()

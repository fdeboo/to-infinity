""" Receives a signal whenever the BookingLineIem is saved """
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OrderLineItem


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update booking total on lineitem update/create
    """
    instance.order.update_total()

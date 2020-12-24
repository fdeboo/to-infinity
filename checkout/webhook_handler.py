"""
Methods handle the different webhook responses from stripe and return
a HTTP response.
"""

import time
from django.http import HttpResponse
from bookings.models import Booking


class StripeWH_Handler:
    """
    Handle Stripe webhooks
    """

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}', status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe.
        Check if the form submission updated the database and if not,
        manually update the booking.
        """

        intent = event.data.object
        booking_id = intent.metadata.booking
        booking = Booking.objects.get(id=booking_id)
        attempt = 1
        while attempt <= 5:
            if booking.status == "COMPLETE":
                break
            else:
                attempt += 1
                time.sleep(1)
        if booking.status == "COMPLETE":
            return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: \
                    Verified booking status has already been updated',
                    status=200,
                )
        else:
            try:
                booking.status = "COMPLETE"
                booking.save()
            except Exception as e:
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500,
                )
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created \
                order in webhook',
            status=200,
        )

    def handle_payment_intent_failed(self, event):
        """
        Handle the payment_intent.failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}', status=200
        )

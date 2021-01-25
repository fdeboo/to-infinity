"""
Methods handle the different webhook responses from stripe and return
a HTTP response.
"""

import time
import datetime
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from products.models import Product
from bookings.models import Booking, BookingLineItem
from profiles.models import UserProfile


class StripeWH_Handler:
    """
    Handle Stripe webhooks
    """

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, booking):
        """Send the user a confirmation email"""
        cust_email = booking.email
        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"booking": booking},
        )
        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {"order": booking, "contact_email": settings.DEFAULT_FROM_EMAIL},
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [cust_email])

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
        pid = intent.id
        print(intent)
        booking_items = intent.metadata.booking_items
        if 'booking' in intent.metadata:
            booking_exists = True
            booking_pk = intent.metadata.booking
            booking = Booking.objects.get(pk=booking_pk)
            print(booking_pk)
        else:
            booking_exists = False
        contact_details = intent.charges.data[0].billing_details
        username = intent.metadata.username
        profile = UserProfile.objects.get(user__username=username)
        print(profile)

        # Clean data in the contact_details
        for field, value in contact_details.items():
            if value == "":
                contact_details[field] = None

        attempt = 1
        while attempt <= 5:
            if booking_exists:
                if booking.status == "COMPLETE":
                    break
                else:
                    attempt += 1
                    time.sleep(1)
            else:
                try:
                    booking = Booking.objects.get(
                        full_name__iexact=contact_details.name,
                        contact_email__iexact=contact_details.email,
                        contact_number__iexact=contact_details.phone,
                        original_bag=booking_items,
                        stripe_pid=pid,
                        status="COMPLETE"
                    )
                    booking_exists = True
                    break
                except Booking.DoesNotExist:
                    attempt += 1
                    time.sleep(1)

        print(booking_exists)
        print(booking.status)

        if booking_exists and booking.status == 'COMPLETE':
            # self._send_confirmation_email(booking)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: \
                Verified booking status has already been updated',
                status=200,
            )
        else:
            booking = None
            try:
                booking = Booking.objects.create(
                    full_name__iexact=contact_details.name,
                    contact_email__iexact=contact_details.email,
                    contact_number__iexact=contact_details.phone,
                    original_bag=booking_items,
                    lead_passenger=profile,
                    stripe_pid=pid,
                    status="COMPLETE",
                    date_completed=datetime.datetime.now()
                )
                for product_id, quantity in booking_items.items():
                    product = Product.objects.get(pk=product_id)
                    booking_line_item = BookingLineItem(
                        booking=booking,
                        product=product,
                        quantity=quantity,
                    )
                    booking_line_item.save()

            except Exception as e:
                if booking:
                    booking.delete()
                    return HttpResponse(
                        content=f'Webhook received: \
                                {event["type"]} | ERROR: {e}',
                        status=500,
                    )

        # self._send_confirmation_email(booking)
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

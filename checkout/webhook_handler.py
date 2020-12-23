import time
from django.http import HttpResponse
from profiles.models import UserProfile
from bookings.models import Booking


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
            {"booking": booking, "contact_email": settings.DEFAULT_FROM_EMAIL},
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
        Handle the payment_intent.succeeded webhook from Stripe
        """

        intent = event.data.object
        pid = intent.id
        lineitems = intent.metadata.items
        booking_id = intent.metadata.booking_id
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        billing_address = intent.billing_details.address
        booking_total = round(intent.charges.data[0].amount / 100, 2)

        profile = None
        username = intent.metadata.username
        profile = UserProfile.objects.get(user__username=username)
        if save_info:
            profile.default_phone_number = billing_address.phone
            profile.default_country = billing_address.address.country
            profile.default_postcode = billing_address.address.postal_code
            profile.default_town_or_city = billing_address.address.city
            profile.default_street_address1 = (
                billing_address.address.line1
            )
            profile.default_street_address2 = (
                billing_address.address.line2
                )
            profile.default_county = billing_address.address.state
            profile.save()

        booking_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                complete_bookings = Booking.objects.filter(status="COMPLETE")
                if complete_bookings:
                    booking = complete_bookings.get(id=booking_id)
                    booking_exists = True
                    break
                else:
                    attempt += 1
                    time.sleep(1)
            except booking.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if booking_exists:
            self._send_confirmation_email(booking)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified booking already in database',
                status=200,
            )

        else:
            booking = None
            try:
                booking = Booking.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        booking_line_item = BookingLineItem(
                            booking=booking,
                            product=product,
                            quantity=item_data,
                        )
                        booking_line_item.save()
                    else:
                        for size, quantity in item_data[
                            "items_by_size"
                        ].items():
                            booking_line_item = bookingLineItem(
                                booking=booking,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            booking_line_item.save()
            except Exception as e:
                if booking:
                    booking.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500,
                )

        self._send_confirmation_email(booking)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created booking in webhook',
            status=200,
        )

    def handle_payment_intent_failed(self, event):
        """
        Handle the payment_intent.failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}', status=200
        )

from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from bookings.models import Booking, BookingLineItem, UserProfile
from .forms import BookingPaymentForm


@method_decorator(login_required, name="dispatch")
class CompleteBookingView(UpdateView):
    """ A view to complete the booking and fill out payment information """
    model = Booking
    form_class = BookingPaymentForm
    template_name = "checkout/checkout.html"

    def get_initial(self):
        # Provide initial values for the form
        initial = super(CompleteBookingView, self).get_initial()
        if self.request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=self.request.user)
                initial.update({
                    "full_name": profile.user.get_full_name(),
                    "email": profile.user.email,
                    "phone_number": profile.default_phone_number,
                    "country": profile.default_country,
                    "postcode": profile.default_postcode,
                    "town_or_city": profile.default_town_or_city,
                    "street_address1": profile.default_street_address1,
                    "street_address2": profile.default_street_address2,
                    "county": profile.default_county,
                })
            except UserProfile.DoesNotExist:
                pass
        else:
            pass
        return initial

    def get_context_data(self, **kwargs):
        """ Retrieves the booking so far """

        stripe_public_key = settings.STRIPE_PUBLIC_KEY

        booking = self.get_object()
        order_items = BookingLineItem.objects.filter(booking=booking.pk)
        addon_items = order_items.filter(product__category=1)
        insurance_items = order_items.filter(product__category=2)
        trip_items = order_items.filter(product__category=3)

        # Add data to the get_context_data dictionary
        data = super(CompleteBookingView, self).get_context_data(**kwargs)
        data["booking"] = booking
        data["order_items"] = order_items
        data["trip_items"] = trip_items
        data["addon_items"] = addon_items
        data["insurance_items"] = insurance_items
        data["stripe_public_key"] = stripe_public_key
        return data

from django.views.generic import UpdateView, View
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import reverse, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
import stripe
from bookings.models import Booking, BookingLineItem, UserProfile
from .forms import BookingPaymentForm


@method_decorator(login_required, name="dispatch")
class CompleteBookingView(UpdateView):
    """ A view to complete the booking with payment information """

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
        stripe_secret_key = settings.STRIPE_SECRET_KEY

        booking = self.get_object()
        order_items = BookingLineItem.objects.filter(booking=booking.pk)
        addon_items = order_items.filter(product__category=1)
        insurance_items = order_items.filter(product__category=2)
        trip_items = order_items.filter(product__category=3)
        stripe_total = round(booking.booking_total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY
        )

        if not stripe_public_key:
            messages.warning(
                self.request,
                "Stripe public ley is missing. \
                Did you forget to set it in your environment?",
            )

        # Add data to the get_context_data dictionary
        data = super(CompleteBookingView, self).get_context_data(**kwargs)
        data["booking"] = booking
        data["order_items"] = order_items
        data["trip_items"] = trip_items
        data["addon_items"] = addon_items
        data["insurance_items"] = insurance_items
        data["stripe_public_key"] = stripe_public_key
        data["client_secret"] = intent.client_secret
        return data

    def form_valid(self, form):
        print(self.object)
        self.object = form.save()
        return super(CompleteBookingView, self).form_valid(form)

    def get_success_url(self):
        booking = self.get_object()
        print(booking)
        return reverse("complete_booking", args=(booking.id,))

    def form_invalid(self, form):
        messages.add_message(
                self.request, messages.WARNING, "Check the form errors."
            )
        return super(CompleteBookingView, self).form_invalid(form)


class CheckoutSuccessView(SingleObjectMixin, View):
    """ Handle successful checkouts """

    def get(self, request):
        save_info = self.request.session.get("save_info")
        booking = self.get_object()

        messages.success(
            self.request,
            f"Booking successfully processed! \
            Your booking number is {booking.booking_ref}. A confirmation \
            email will be sent to {booking.email}.",
        )

        if "passengers" in self.request.session:
            del self.request.session["passengers"]

        template = "checkout/checkout_success.html"
        context = {
            "booking": booking,
        }

        return render(request, template, context)

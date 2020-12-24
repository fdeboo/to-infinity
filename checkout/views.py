import stripe
from django.views.generic import View, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.http import require_POST
from django.shortcuts import reverse, render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
from bookings.models import Booking, BookingLineItem, UserProfile
#  from .models import Billing
from .forms import BookingPaymentForm
#  from profiles.forms import UserProfileForm


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe_api_key = settings.STRIPE_SECRET_KEY
        booking_id = request.POST.get('booking_id')
        stripe.PaymentIntent.modify(pid, metadata={
            'booking': booking_id,
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            "Sorry, your payment cannot be \
            processed right now. Please try again later.",
        )
        return HttpResponse(content=e, status=400)


@method_decorator(login_required, name="dispatch")
class CheckoutView(FormView):
    """ A view to complete the booking with payment information """

    # model = Billing
    form_class = BookingPaymentForm
    template_name = "checkout/checkout.html"

    def get_object(self, request, *args, **kwargs):
        booking = Booking.objects.get(pk=self.kwargs.get('pk'))
        return booking

    def get_initial(self):
        # Provide initial values for the form
        initial = super(CheckoutView, self).get_initial()
        if self.request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=self.request.user)
                initial.update({
                    "full_name": profile.user.get_full_name(),
                    "email": profile.user.email,
                    "phone_number": profile.default_phone_number,
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

        booking = self.get_object(self.request)
        booking_items = BookingLineItem.objects.filter(booking=booking.pk)
        addon_items = booking_items.filter(product__category=1)
        insurance_items = booking_items.filter(product__category=2)
        trip_items = booking_items.filter(product__category=3)
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
        data = super(CheckoutView, self).get_context_data(**kwargs)
        data["booking"] = booking
        data["booking_items"] = booking_items
        data["trip_items"] = trip_items
        data["addon_items"] = addon_items
        data["insurance_items"] = insurance_items
        data["stripe_public_key"] = stripe_public_key
        data["client_secret"] = intent.client_secret
        return data

    def form_valid(self, form):
        pid = self.request.POST.get('client_secret').split('_secret')[0]
        # billing = form.save(commit=False)
        booking = self.get_object(self.request)
        booking_items = BookingLineItem.objects.filter(booking=booking)
        booking.stripe_pid = pid
        original_bag = list(booking_items.values())
        print(original_bag)
        booking.original_bag = original_bag
        booking.save()
        return super(CheckoutView, self).form_valid(form)

    def get_success_url(self):
        booking = self.get_object(self.request)
        return reverse("checkout_success", args=(booking.id,))

    def form_invalid(self, form):
        messages.add_message(
                self.request, messages.WARNING, "Check the form errors."
            )
        return super(CheckoutView, self).form_invalid(form)


class CheckoutSuccessView(SingleObjectMixin, View):
    """ Handle successful checkouts """
    model = Booking

    def get(self, request, *args, **kwargs):

        # save_info = self.request.session.get("save_info")
        booking = Booking.objects.get(pk=self.kwargs['pk'])
        # order = Billing.objects.get(booking=booking.pk)
        profile = UserProfile.objects.get(user=request.user)

        # Attach the user's profile to the order
        # booking.user_profile = profile
        booking.status = "COMPLETE"
        booking.save()

        # Save the user's info
        """ if save_info:
            profile_data = {
                "default_phone_number": order.phone_number,
                "default_country": order.country,
                "default_postcode": order.postcode,
                "default_town_or_city": order.town_or_city,
                "default_street_address1": order.street_address1,
                "default_street_address2": order.street_address2,
                "default_county": order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save() """
        messages.success(
            self.request,
            f"Booking successfully processed! \
            Your booking number is {booking.booking_ref}. A confirmation \
            email will be sent to {profile.user.email}.",
        )

        if "passengers" in self.request.session:
            del self.request.session["passengers"]

        template = "checkout/checkout-success.html"
        context = {
            "booking": booking
        }

        return render(request, template, context)

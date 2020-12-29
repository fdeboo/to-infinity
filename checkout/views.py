"""
Views required for the checkout process. Provide the context for a booking
summary and form to collect payment details for Stripe. Updates booking status
if checkout successful.
"""

import json
import datetime
import stripe
from django.views.generic import View, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.http import require_POST
from django.shortcuts import reverse, render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
from products.models import Product
from bookings.models import Booking, BookingLineItem, UserProfile
from .forms import BookingPaymentForm


@require_POST
def cache_checkout_data(request):
    """ Add metadata to Payment intent so that it can be accessed in
    webhook handling """

    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        save_info = request.POST.get('save_info')
        stripe.PaymentIntent.modify(pid, metadata={
            "booking_items": json.dumps(
                request.session.get("booking_items", {})
                ),
            "booking": request.session.get("booking", ""),
            "save_info": save_info,
        })
        request.session['save_info'] = save_info
        del request.session["booking"]
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

    form_class = BookingPaymentForm
    template_name = "checkout/checkout.html"

    def get_object(self, request, **kwargs):
        """ Retrieves the primary key from the kwargs to use for lookup """

        booking = Booking.objects.get(pk=self.kwargs.get('pk'))
        return booking

    def get_initial(self):
        # Provide initial values for the form
        initial = super(CheckoutView, self).get_initial()
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            initial.update({
                "full_name": profile.user.get_full_name(),
                "email": profile.user.email,
                "phone_number": profile.default_phone_num,
            })
        except UserProfile.DoesNotExist:
            pass
        return initial

    def get_context_data(self, **kwargs):
        """ Retrieves the booking so far """

        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY

        booking = self.get_object(self.request)
        items = self.request.session.get("booking_items")
        booking_items = []
        addon_items = []
        trip_items = []
        # insurance+items = []
        booking_total = 0
        for product_id, quantity in items.items():
            product = Product.objects.get(pk=product_id)
            item = {
                'product': product,
                'quantity': quantity,
                'line_total': (product.price * quantity)
            }
            booking_total += item['line_total']
            booking_items.append(item)
            if product.category.pk == 1:
                addon_items.append(item)
                # elif product.category.pk == 2:
                #    insurance_items.append(item)
            elif product.category.pk == 3:
                trip_items.append(item)
            else:
                pass
        stripe_total = round(booking_total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY
        )

        if not stripe_public_key:
            messages.warning(
                self.request,
                "Stripe public key is missing. \
                Did you forget to set it in your environment?",
            )
        self.request.session['booking'] = booking.pk

        # Add data to the get_context_data dictionary
        data = super(CheckoutView, self).get_context_data(**kwargs)
        data["booking_total"] = booking_total
        data["booking_items"] = booking_items
        data["trip_items"] = trip_items
        data["addon_items"] = addon_items
        # data["insurance_items"] = insurance_items
        data["stripe_public_key"] = stripe_public_key
        data["client_secret"] = intent.client_secret
        return data

    def form_valid(self, form):
        pid = self.request.POST.get('client_secret').split('_secret')[0]
        booking = self.get_object(self.request)
        booking.contact_number = form.cleaned_data['phone_number']
        booking.date_completed = datetime.datetime.now()
        booking.stripe_pid = pid
        booking_items = self.request.session.get('booking_items', {})
        booking.original_bag = json.dumps(booking_items)
        for product_id, quantity in booking_items.items():
            product = Product.objects.get(pk=product_id)
            booking_line_item = BookingLineItem(
                booking=booking,
                product=product,
                quantity=quantity,
            )
            booking_line_item.save()
        booking.status = "COMPLETE"
        booking.save()

        # save the save_info input to the session
        return super(CheckoutView, self).form_valid(form)

    def get_success_url(self):
        booking = self.get_object(self.request)
        return reverse("checkout_success", args=(booking.pk,))

    def form_invalid(self, form):
        messages.add_message(
                self.request, messages.WARNING, "Check the form errors."
            )
        return super(CheckoutView, self).form_invalid(form)


class CheckoutSuccessView(SingleObjectMixin, View):
    """ Handle successful checkouts """

    def get(self, request, *args, **kwargs):
        """ Get the booking instance from the kwargs and update the
        the booking status to 'complete'. """

        save_info = self.request.session.get("save_info")
        booking = Booking.objects.get(pk=self.kwargs['pk'])
        profile = UserProfile.objects.get(user=request.user)
        print(profile)
        if save_info == "true":
            profile.default_phone_num = booking.contact_number
            profile.save()

        messages.success(
            self.request,
            f"Booking successfully processed! \
            Your booking number is {booking.booking_ref}. A confirmation \
            email will be sent to {profile.user.email}.",
        )

        # Delete values from the session that are redundant
        if "save_info" in self.request.session:
            del self.request.session["save_info"]
        if "booking_items" in self.request.session:
            del self.request.session["booking_items"]
        if "destination_choice" in self.request.session:
            del self.request.session["destination_choice"]
        if "request_date" in self.request.session:
            del self.request.session["request_date"]
        if self.request.session["passenger_total"]:
            del self.request.session["passenger_total"]

        template = "checkout/checkout-success.html"
        context = {
            "booking": booking
        }

        return render(request, template, context)

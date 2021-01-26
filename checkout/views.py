"""
Views required for the checkout process. Provide the context for a booking
summary and form to collect payment details for Stripe. Updates booking status
if checkout successful.
"""

from datetime import datetime
import json
import ast
import stripe
from django.views.generic import View
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.views.generic.detail import (
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
)
from django.views.decorators.http import require_POST
from django.shortcuts import reverse, render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
from products.models import Product, AddOn
from bookings.models import Booking, BookingLineItem, Passenger, Trip
from profiles.models import UserProfile
from .forms import BookingCheckoutForm


@require_POST
def cache_checkout_data(request):
    """Add metadata to Payment intent so that it can be accessed in
    webhook handling"""

    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        save_info = request.POST.get("save_info")
        booking = request.session.get("booking", "")
        if booking:
            print("yes")
            stripe.PaymentIntent.modify(
                pid,
                metadata={
                    "booking_items": json.dumps(
                        request.session.get("booking_items", {})
                    ),
                    "booking": booking,
                    "username": request.user,
                    "save_info": save_info,
                },
            )
        else:
            print("no")
            stripe.PaymentIntent.modify(
                pid,
                metadata={
                    "booking_items": json.dumps(
                        request.session.get("booking_items", {})
                    ),
                    "username": request.user,
                    "save_info": save_info,
                },
            )
        request.session["save_info"] = save_info
        if "booking" in request.session:
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
class CheckoutView(
    SingleObjectTemplateResponseMixin, ModelFormMixin, ProcessFormView
):
    """
    A view to complete the booking with payment information.
    Checks if a pk is in the url. This establishes whether the booking instance
    already exisits in the database as an open booking - in which case it will
    be 'updated' to COMPLETE - otherwise the booking instance will be 'created'
    at checkout.
    """

    model = Booking
    form_class = BookingCheckoutForm
    template_name = "checkout/checkout.html"

    def __init__(self):
        self.object = None
        self.trip = None

    def get(self, request, *args, **kwargs):
        """ Check if pk in url and if not set to None. """
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is None:
            self.object = None
            booking = None
            booking_model = self.request.session.get('booking_model', {})
            trip_pk = booking_model['trip']
        else:
            self.object = self.get_object()
            booking = Booking.objects.get(pk=pk)
            original_bag = booking.original_bag
            trip_pk = booking.trip.pk
            passenger_count = Passenger.objects.filter(
                booking=booking.pk).count()
            self.request.session["passenger_total"] = passenger_count
            self.request.session["booking"] = booking.pk
            self.request.session["booking_items"] = ast.literal_eval(
                original_bag
            )
        trip = Trip.objects.get(pk=trip_pk)
        passenger_total = self.request.session["passenger_total"]
        print(passenger_total)
        print(trip.seats_available)

        # Prepare trip date for comparison by making it a naive date
        date_attr = trip.date
        date_string = date_attr.strftime("%Y-%m-%d")
        datetime_naive = datetime.strptime(date_string, "%Y-%m-%d")

        # Check to see if the date is in the past
        if datetime_naive < datetime.today():
            if booking:
                booking.delete()
            template_name = "checkout/date-passed.html"
            context = {
                "date": trip.date,
            }
            return render(request, template_name, context)

        # Check to see if there are still seats available on the trip
        if trip.seats_available < passenger_total:
            template_name = "checkout/seats-unavailable.html"
            context = {
                "destination": trip.destination,
                "date": trip.date,
                "passengers": passenger_total,
            }
            return render(request, template_name, context)

        return super(CheckoutView, self).get(request, *args, **kwargs)

    def get_object(self, **kwargs):
        """ Retrieve the primary key from the kwargs to use for lookup"""
        booking = self.model.objects.get(pk=self.kwargs.get("pk"))
        return booking

    def get_initial(self):
        # Provide initial values for the form
        initial = super(CheckoutView, self).get_initial()
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            initial.update(
                {
                    "full_name": profile.user.get_full_name(),
                    "contact_email": profile.user.email,
                    "contact_number": profile.default_phone_num,
                }
            )
        except UserProfile.DoesNotExist:
            pass
        return initial

    def get_context_data(self, **kwargs):
        """ Retrieves the booking so far """

        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY

        items = self.request.session.get("booking_items")
        booking_items = []
        addon_items = []
        trip_items = []
        # insurance+items = []
        booking_total = 0
        for product_id, quantity in items.items():
            product = Product.objects.get(pk=product_id)
            item = {
                "product": product,
                "quantity": quantity,
                "line_total": (product.price * quantity),
            }
            booking_total += item["line_total"]
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
            amount=stripe_total, currency=settings.STRIPE_CURRENCY
        )

        if not stripe_public_key:
            messages.warning(
                self.request,
                "Stripe public key is missing. \
                Did you forget to set it in your environment?",
            )

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

    def post(self, request, *args, **kwargs):
        # Check if pk in url and if not set to none

        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is None:
            self.object = None
        else:
            self.object = self.get_object()
        return super(CheckoutView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        pid = self.request.POST.get("client_secret").split("_secret")[0]
        self.object = form.save(commit=False)
        self.object.date_completed = datetime.now()
        self.object.stripe_pid = pid
        booking_items = self.request.session.get("booking_items", {})
        self.object.original_bag = json.dumps(booking_items)
        self.object.status = "COMPLETE"
        self.object.save()
        for product_id, quantity in booking_items.items():
            product = Product.objects.get(pk=product_id)
            booking_line_item = BookingLineItem(
                booking=self.object,
                product=product,
                quantity=quantity,
            )
            booking_line_item.save()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is None:
            booking_model = self.request.session.get('booking_model', {})
            trip_pk = booking_model['trip']
            trip = Trip.objects.get(pk=trip_pk)
            self.object.trip = trip
            self.object.lead_passenger = UserProfile.objects.get(
                user=self.request.user
            )
            self.object.save()
            passenger_details = self.request.session.get(
                'passenger_details', {}
            )
            for passenger in passenger_details:
                addons = passenger['addons']
                addon_qs = None
                for addon in addons:
                    item = AddOn.objects.filter(pk=addon)
                    if addon_qs is None:
                        addon_qs = item
                    else:
                        addon_qs = addon_qs | item
                new_passenger = Passenger(
                    booking=self.object,
                    first_name=passenger['fname'],
                    last_name=passenger['lname'],
                    email=passenger['email'],
                    passport_no=passenger['passport'],
                    is_leaduser=passenger['is_leaduser'],
                )
                new_passenger.save()
                if addon_qs:
                    new_passenger.trip_addons.set(addon_qs)

        else:
            booking = Booking.objects.get(pk=pk)
            booking.trip.update_seats_available()

        # save the save_info input to the session
        return super(CheckoutView, self).form_valid(form)

    def get_success_url(self):
        """
        Defines the view that the user should be forwarded to and passes the
        booking pk as an argument
        """

        booking = self.object
        return reverse("checkout_success", args=(booking.pk,))

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.WARNING, "Check the form errors."
        )
        return super(CheckoutView, self).form_invalid(form)


class CheckoutSuccessView(SingleObjectMixin, View):
    """ Handle successful checkouts """

    def get(self, request, *args, **kwargs):
        """Get the booking instance from the kwargs and update the
        the booking status to 'complete'."""

        save_info = self.request.session.get("save_info")
        booking = Booking.objects.get(pk=self.kwargs["pk"])
        profile = UserProfile.objects.get(user=request.user)
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
        if "passenger_total" in self.request.session:
            del self.request.session["passenger_total"]

        template = "checkout/checkout-success.html"
        context = {"booking": booking}

        return render(request, template, context)

"""
Views in this module provide logic for templates that guide the booking process
"""

import json
import ast
from datetime import datetime
from django.shortcuts import redirect, render, reverse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView, CreateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from products.models import Product
from .formset import make_passenger_formset
from .models import (
    Trip,
    Booking,
    Passenger,
    Destination,
    UserProfile,
)
from .forms import (
    SearchTripsForm,
    DateChoiceForm,
    InputPassengersForm,
    make_passenger_form,
)


@method_decorator(login_required, name="dispatch")
class SearchTripsView(FormView):
    """
    Renders an initial search form for users to search availabiltiy for
    trips to a destination
    """

    template_name = "bookings/search_trips.html"
    form_class = SearchTripsForm

    def get_initial(self):
        """
        Checks to see if data is already in session and if so, sets the initial
        values for the form.
        """
        initial = super().get_initial()
        if "request_date" in self.request.session:
            date = self.request.session["request_date"]
            form_date = json.loads(date)
            initial["request_date"] = form_date
        else:
            pass

        if "destination_choice" in self.request.session:
            form_destination = self.request.session["destination_choice"]
            initial["destination"] = form_destination
        else:
            pass
        if "passenger_total" in self.request.session:
            form_passengers = self.request.session["passenger_total"]
            initial["passengers"] = form_passengers
        else:
            pass
        return initial

    def form_valid(self, form):
        date = form.cleaned_data["request_date"]
        date = json.dumps(date, cls=DjangoJSONEncoder)
        self.request.session["request_date"] = date
        self.request.session["destination_choice"] = form.cleaned_data[
            "destination"
        ].pk
        self.request.session["passenger_total"] = form.cleaned_data[
            "passengers"
        ]

        return HttpResponseRedirect(reverse("confirm_trip"))


@method_decorator(login_required, name="dispatch")
class ConfirmTripView(FormView):
    """
    Provides the user a set of choice options based on their search input in
    the products.TripsView
    """

    model = Booking
    template_name = "bookings/trips_available.html"
    form_class = DateChoiceForm

    def __init__(self):
        self.searched_date = None
        self.passengers = None
        self.destination_pk = None
        self.gte_dates = None
        self.lt_dates = None

    def get_available_trips(self, destination, passengers):
        """ Find trips with enough seats for searched no. of passengers """

        available_trips = Trip.objects.filter(destination=destination).filter(
            seats_available__gte=passengers
        )
        return available_trips

    def get_trips_matched_or_post_date(self, date, destination, passengers):
        """
        Returns trips that either match or are post- searched_date
        Refine to trips with dates closest to searched_date
        limit to 3 results
        """

        available_trips = self.get_available_trips(destination, passengers)
        gte_dates = available_trips.filter(date__gte=date)[:3]
        return gte_dates

    def get_trips_preceding_date(self, date, destination, passengers):
        """
        Returns trips that are pre- searched_date
        Refines to trips with dates closest to searched_date
        limits to 3 results
        """

        available_trips = self.get_available_trips(destination, passengers)
        today = datetime.today()
        lt_dates = (
            available_trips.filter(date__lt=date)
            .filter(date__gt=today)
            .order_by("-date")[:3]
        )
        return lt_dates

    def make_timezone_naive(self, obj):
        """ Turns date attribute to a time-zone naive date object """

        date_attr = obj.date
        date_string = date_attr.strftime("%Y-%m-%d")
        datetime_naive = datetime.strptime(date_string, "%Y-%m-%d")
        return datetime_naive

    def get_trips_queryset(self, gte_dates, lt_dates):
        """Creates the queryset that will be used by the ModelChoiceField
        in the DateChoiceForm"""

        # Merge both queries
        trips = lt_dates | gte_dates
        trips = trips.order_by("date")
        return trips

    def get(self, request, *args, **kwargs):
        """ Checks to see if the values required to render the template are
        available and if not renders a custom error template"""

        # Check if the required session data exists
        if not all(
            x in self.request.session for x in [
                'request_date', 'passenger_total', 'destination_choice']
        ):
            template_name = "bookings/session-unavailable.html"
            context = {}
            return render(request, template_name, context)

        # Retrieve values from the session
        date = self.request.session["request_date"]
        self.searched_date = json.loads(date)
        self.passengers = self.request.session["passenger_total"]
        self.destination_pk = self.request.session["destination_choice"]

        # check for any trips with enough 'seats_available' for the
        # requested number of passengers
        available_trips = self.get_available_trips(
            self.destination_pk, self.passengers
        )
        if not available_trips:
            template_name = "bookings/unavailable.html"
            destination = Destination.objects.get(pk=self.destination_pk)
            context = {
                "destination": destination,
                "passengers": self.passengers,
            }
            return render(request, template_name, context)
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        """
        Finds the closest available date relative to searched date to use
        as intial selected value in the form
        """

        # Retrieve values from the session
        date = self.request.session.get("request_date", "")
        self.searched_date = json.loads(date)
        self.passengers = self.request.session.get("passenger_total", "")
        self.destination_pk = self.request.session.get(
            "destination_choice", ""
        )
        # Return querysets for dates before/beyond searched_date respectively:
        self.gte_dates = self.get_trips_matched_or_post_date(
            self.searched_date, self.destination_pk, self.passengers
        )
        self.lt_dates = self.get_trips_preceding_date(
            self.searched_date, self.destination_pk, self.passengers
        )

        naive_searched_date = datetime.strptime(self.searched_date, "%Y-%m-%d")
        # Find the trip closest to the searched_date (for form initial value)
        if self.gte_dates:
            gte_date = self.gte_dates[0]
            naive_gte_date = self.make_timezone_naive(gte_date)
            if self.lt_dates:
                lt_date = self.lt_dates[0]
                naive_lt_date = self.make_timezone_naive(lt_date)

                if (
                    naive_gte_date - naive_searched_date
                    > naive_searched_date - naive_lt_date
                ):
                    default_selected = lt_date
                else:
                    default_selected = gte_date

            else:
                default_selected = gte_date

        elif self.lt_dates:
            lt_date = self.lt_dates[0]
            default_selected = lt_date

        else:
            messages.error(
                self.request,
                "Sorry, there are no dates currently available for the"
                "selected destination.",
            )
            return redirect("home.home")

        # Provide initial values for the form
        initial = super().get_initial()
        initial.update({"trip": default_selected})
        return initial

    def get_form_kwargs(self, **kwargs):
        """ Provides keyword arguemnts """
        kwargs = super().get_form_kwargs()
        trips = self.get_trips_queryset(self.gte_dates, self.lt_dates)
        kwargs.update({"trips": trips})
        return kwargs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        destination = Destination.objects.filter(pk=self.destination_pk)
        context.update(
            {
                "passengers": self.passengers,
                "destination_obj": destination,
                "date": self.searched_date,
            }
        )
        return context

    def form_valid(self, form):
        """
        Takes the POST data from the DateChoiceForm and creates an
        Intitial Booking in the session.
        """

        # Create object to store data relevant to the booking
        booking_model = {}

        # Create object to store data relevant to the products for purchase
        booking_items = {}
        trip = form.cleaned_data["trip"]
        destination = trip.destination
        product_id = destination.product_id
        quantity = self.passengers
        booking_items[product_id] = quantity
        booking_model["trip"] = trip.pk

        # Save both objects to the session
        self.request.session["booking_model"] = booking_model
        self.request.session["booking_items"] = booking_items

        return redirect("create_passengers")


@method_decorator(login_required, name="dispatch")
class InputPassengersView(CreateView):
    """
    A view to create the passenger details that will be added to the booking.
    Number of formsets =  number of passengers in search
    """

    model = Booking
    form_class = InputPassengersForm
    template_name = "bookings/passenger_details.html"

    def __init__(self):
        self.trip = None
        self.object = None
        self.cancel = False
        self.save = False
        self.profile = None

    def get(self, request, *args, **kwargs):
        """ Checks to see if the values required to render the template are
        available and if not renders a custom error template"""

        # Check if the required session data exists
        if not all(
            x in self.request.session for x in [
                'passenger_total', 'booking_model', 'booking_items']
        ):
            template_name = "bookings/session-unavailable.html"
            context = {}

            return render(request, template_name, context)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Get data from the session that will be used to define the forms
        passenger_total = self.request.session["passenger_total"]
        trip_pk = self.request.session["booking_model"]["trip"]
        self.trip = Trip.objects.get(pk=trip_pk)

        # Pass trip data to the formset to determine the addon options
        passenger_form = make_passenger_form(self.trip)

        # Pass passenger_total to determine number of forms
        formset = make_passenger_formset(passenger_form, passenger_total)
        data = super().get_context_data(**kwargs)
        self.profile = UserProfile.objects.get(user=self.request.user)

        # Provide the context for the booking summary
        items = self.request.session.get("booking_items", "")
        trip_items = []
        booking_total = 0
        for product_id, quantity in items.items():
            product = Product.objects.get(pk=product_id)
            item = {
                "product": product,
                "quantity": quantity,
                "line_total": (product.price * quantity),
            }
            if product.category.pk == 3:
                booking_total += item["line_total"]
                trip_items.append(item)

        if self.request.POST:
            data["profile"] = self.profile
            data["booking_total"] = booking_total
            data["trip_items"] = trip_items
            data["passenger_formset"] = formset(self.request.POST)
        else:
            data["profile"] = self.profile
            data["booking_total"] = booking_total
            data["trip_items"] = trip_items
            data["passenger_formset"] = formset(
                initial=[
                    {
                        "first_name": self.profile.user.first_name,
                        "last_name": self.profile.user.last_name,
                        "email": self.profile.user.email,
                        "passport_no": self.profile.default_passport_num,
                    }
                ],
            )
        return data

    def get_initial(self):
        initial = super().get_initial()
        initial.update({"trip": self.trip})
        return initial

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if "cancel" in form.data:
            self.cancel = True
            if "booking_items" in self.request.session:
                del self.request.session["booking_items"]
            if "booking_model" in self.request.session:
                del self.request.session["booking_model"]
            if "destination_choice" in self.request.session:
                del self.request.session["destination_choice"]
            if "request_date" in self.request.session:
                del self.request.session["request_date"]
            if "passenger_total" in self.request.session:
                del self.request.session["passenger_total"]
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super().post(
                request, *args, **kwargs
            )

    def form_valid(self, form):
        """
        Checks which sumbit button was clicked and saves validated form data
        to either the session or to the database.
        Identifies the lead_passenger and sets their 'is_leadpassenger' status
        to True.
        """

        context = self.get_context_data()
        formset = context["passenger_formset"]
        booking_items = self.request.session["booking_items"]

        # Check to see if form was 'saved for later'
        if "save" in form.data:
            lead_passenger_id = None
            self.save = True
            self.object = form.save()
            if formset.is_valid():
                for count, form in enumerate(formset):
                    lead_passenger = False
                    if count == 0:
                        lead_passenger_id = form.cleaned_data["passport_no"]
                    addons = form.cleaned_data["trip_addons"]
                    for addon in addons:
                        product_id = addon.product_id
                        quantity = 1
                        if product_id in booking_items:
                            quantity += booking_items.get(product_id)
                        booking_items[product_id] = quantity
                formset.instance = self.object
                formset.save()
                booking = self.object
                booking.status = "OPENED"
                booking.original_bag = booking_items
                booking.lead_user = self.profile
                booking.save()
                lead_passenger = Passenger.objects.filter(
                    booking=booking.pk).get(passport_no=lead_passenger_id)
                lead_passenger.is_leadpassenger = True
                lead_passenger.save()
                messages.add_message(
                    self.request, messages.SUCCESS, "Changes were saved."
                )
                return super().form_valid(form)
            else:
                messages.add_message(
                    self.request, messages.WARNING, "Check the form errors."
                )
                return super().form_invalid(form)

        else:
            # Else, save the form data to the session and proceed
            self.object = form.save(commit=False)
            passenger_details = []
            if formset.is_valid():
                for count, form in enumerate(formset):
                    lead_passenger = False
                    if count == 0:
                        lead_passenger = True
                    addons = form.cleaned_data["trip_addons"]
                    addon_set = []
                    for addon in addons:
                        addon_set.append(addon.pk)
                        product_id = addon.product_id
                        quantity = 1
                        if product_id in booking_items:
                            quantity += booking_items.get(product_id)
                        booking_items[product_id] = quantity
                    passenger = {
                        "fname": form.cleaned_data["first_name"],
                        "lname": form.cleaned_data["last_name"],
                        "email": form.cleaned_data["email"],
                        "passport": form.cleaned_data["passport_no"],
                        "is_lead": lead_passenger,
                        "addons": addon_set,
                    }
                    passenger_details.append(passenger)
                self.request.session["passenger_details"] = passenger_details
                messages.add_message(
                    self.request, messages.SUCCESS, "Changes were saved."
                )
                return HttpResponseRedirect(self.get_success_url())
            else:
                messages.add_message(
                    self.request, messages.WARNING, "Check the form errors."
                )
                return super().form_invalid(form)

    def get_success_url(self):
        if self.cancel:
            return reverse("home")
        if self.save:
            return reverse("profile")
        else:
            return reverse("create_order")

    def form_invalid(self, form):
        messages.add_message(
            self.request, messages.error, "There was a problem."
        )


class CancelBookingView(DeleteView):
    """ Deletes the booking instance passed in the post request """

    model = Booking
    success_url = reverse_lazy("profile")

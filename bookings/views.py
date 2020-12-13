"""
Views in this module provide logic for templates that guide the booking process
"""

import json
from datetime import datetime
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.views import View
from django.views.generic import FormView, UpdateView
from django.forms import inlineformset_factory
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import (
    Trip,
    Booking,
    BookingLineItem,
    Destination,
    Passenger,
    UserProfile
)
from .forms import (
    DateChoiceForm,
    PassengerForm,
    InputPassengersForm,
    PassengerFormSetHelper
)


@method_decorator(never_cache, name="dispatch")
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
        self.destination_id = None
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
        lt_dates = available_trips.filter(date__lt=date).order_by("-date")[:3]
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

    def get_initial(self):
        """Retrieves values from session and formulates variables
        to be used in the form"""

        # Retrieve values from the session
        date = self.request.session["request_date"]
        self.searched_date = json.loads(date)
        self.passengers = self.request.session["passenger_total"]
        self.destination_id = self.request.session["destination_choice"]

        # Return querysets for dates before/beyond searched_date respectively:
        self.gte_dates = self.get_trips_matched_or_post_date(
            self.searched_date, self.destination_id, self.passengers
        )
        self.lt_dates = self.get_trips_preceding_date(
            self.searched_date, self.destination_id, self.passengers
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

        # Get initial valuees for the form
        initial = super(ConfirmTripView, self).get_initial()
        initial.update({"trip": default_selected})
        return initial

    def get_form_kwargs(self, **kwargs):
        """ Provides keyword arguemnt """

        kwargs = super(ConfirmTripView, self).get_form_kwargs()

        trips = self.get_trips_queryset(self.gte_dates, self.lt_dates)
        kwargs.update({"trips": trips})
        return kwargs

    def get_context_data(self, **kwargs):

        context = super(ConfirmTripView, self).get_context_data(**kwargs)
        destination = Destination.objects.filter(id=self.destination_id)
        context["passengers"] = self.passengers
        context["destination_obj"] = destination
        return context

    def form_valid(self, form):
        """
        Takes the POST data from the DateChoiceForm and creates an
        Intitial Booking in the database
        """

        booking = form.save(commit=False)
        booking.status = "RESERVED"
        booking.save()
        trip = form.cleaned_data["trip"]
        destination = trip.destination
        booking_line_item = BookingLineItem(
            booking=booking,
            product=destination,
            quantity=self.request.session["passenger_total"],
        )
        booking_line_item.save()
        return redirect("create_passengers", booking.id)


@method_decorator(login_required, name="dispatch")
class InputPassengersView(UpdateView):
    """
    A view to update the booking instance with passenger details,
    number of formsets =  number of passengers in search
    """

    model = Booking
    form_class = InputPassengersForm
    template_name = "bookings/passenger_details.html"

    def get_context_data(self, **kwargs):
        passengers = self.request.session["passenger_total"]
        PassengerFormSet = inlineformset_factory(
            Booking,
            Passenger,
            form=PassengerForm,
            extra=passengers,
            max_num=passengers,
            min_num=passengers,
            validate_max=True,
            validate_min=True,
            can_delete=False

        )
        data = super(InputPassengersView, self).get_context_data(**kwargs)
        helper = PassengerFormSetHelper()
        profile = UserProfile.objects.get(user=self.request.user)
        if self.request.POST:
            data['formset'] = PassengerFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            data['formset'] = PassengerFormSet(
                initial=[{
                    "first_name": profile.user.first_name,
                    "last_name": profile.user.last_name,
                    "email": profile.user.email,
                }],
                instance=self.object
            )
            data['helper'] = helper
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
            formset.save_m2m()

            messages.add_message(
                self.request, messages.SUCCESS, "Changes were saved."
            )

    def get_success_url(self):
        return reverse("complete_booking")


class CompleteBookingView(View):
    template = "checkout.html"
    print("MADE IT")

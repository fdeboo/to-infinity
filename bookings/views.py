"""
Views in this module provide logic for templates that guide the booking process
"""

import json
from datetime import datetime
from django.shortcuts import redirect, render, reverse
from django.contrib import messages
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
    RequiredPassengerFormSet,
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

    def get(self, request, *args, **kwargs):
        # Retrieve values from the session
        date = self.request.session["request_date"]
        self.searched_date = json.loads(date)
        self.passengers = self.request.session["passenger_total"]
        self.destination_pk = self.request.session["destination_choice"]

        # check if any trips with 'seats_available' = the requested number of passengers
        available_trips = self.get_available_trips(
            self.destination_pk,
            self.passengers
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
        destination = Destination.objects.filter(pk=self.destination_pk)
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
        passenger_total = self.request.session["passenger_total"]
        PassengerFormSet = inlineformset_factory(
            Booking,
            Passenger,
            form=PassengerForm,
            formset=RequiredPassengerFormSet,
            extra=passenger_total,
            max_num=passenger_total,
            min_num=passenger_total,
            validate_max=True,
            validate_min=True,
            can_delete=False
        )
        data = super(InputPassengersView, self).get_context_data(**kwargs)
        profile = UserProfile.objects.get(user=self.request.user)
        if self.request.POST:
            data['passenger_formset'] = PassengerFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            data['passenger_formset'] = PassengerFormSet(
                initial=[{
                    "first_name": profile.user.first_name,
                    "last_name": profile.user.last_name,
                    "email": profile.user.email,
                }],
                instance=self.object
            )
        return data

    def form_valid(self, form):
        """ Runs when the form is valid """

        context = self.get_context_data()
        formset = context['passenger_formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super(InputPassengersView, self).form_valid(form)
        else:
            return super(InputPassengersView, self).form_invalid(form)
        messages.add_message(
            self.request, messages.SUCCESS, "Changes were saved."
        )

    def get_success_url(self):
        return reverse("complete_booking", args=(self.object.id,))

    def form_invalid(self, form):
        print('form invalid:failed')


class CompleteBookingView(UpdateView):
    """ A view to complete the booking and fill out payment information """
    template_name = "checkout.html"

    print("MADE IT")

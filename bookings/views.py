""" Views in this module provides logic for templates that guide
the booking process """
from datetime import datetime
from django.shortcuts import render
from django.contrib import messages
from django.views import View
from .models import Trip
from .forms import DateChoiceForm, InitialSearchForm


class TripSelection(View):
    """ A view to show results of search """

    template = "bookings/trips_available.html"
    form_class = DateChoiceForm

    def post(self, request):
        """ Takes the POST data from the POST request """

        form = InitialSearchForm(request.POST)
        if form.is_valid():
            destination_choice = request.POST.get("destination")
            searched_date = request.POST.get("request_date")
            passenger_total = int(request.POST.get("passengers"))

            # Find trips with enough seats for requested no. of passengers
            available_trips = Trip.objects.filter(
                destination=destination_choice
            ).filter(seats_available__gte=passenger_total)

            # Refine to trips with dates closest to searched_date
            # limit to 3 results
            gte_dates = available_trips.filter(
                date__gte=searched_date
            ).order_by("date")[
                :3
            ]  # Returns trips that either match or are post- searched_date

            lt_dates = available_trips.filter(date__lt=searched_date).order_by(
                "-date"
            )[
                :3
            ]  # Returns trips that are pre- searched_date

            # Merge both queries
            trips = gte_dates | lt_dates

            naive_searched_date = datetime.strptime(searched_date, "%Y-%m-%d")

            # Find trip closest to searched_date and make timezone naive
            if gte_dates:
                date_gte = gte_dates[0]
                naive_closest_gte = self.timezone_naive(date_gte)
                if lt_dates:
                    date_lt = lt_dates[0]
                    naive_closest_lt = self.timezone_naive(date_lt)

                    if (
                        naive_closest_gte - naive_searched_date
                        > naive_searched_date - naive_closest_lt
                    ):
                        default_selected = date_lt
                    else:
                        default_selected = date_gte
                else:
                    default_selected = date_gte
            elif lt_dates:
                date_lt = lt_dates[0]
                naive_closest_lt = self.timezone_naive(date_lt)
                default_selected = date_lt
            else:
                messages.error(
                    request,
                    "Sorry, there are no dates currently available for the"
                    "selected destination.",
                )

            form = self.form_class(
                trips=trips,
                initial={
                    "trip_date": default_selected,
                    "num_passengers": passenger_total,
                },
            )
            return render(request, self.template, {"form": form})

    def timezone_naive(self, query_object):
        """ Turns date attributes to a time-zone naive date """

        date_attr = query_object.date
        date_string = date_attr.strftime("%Y-%m-%d")
        date_obj_naive = datetime.strptime(date_string, "%Y-%m-%d")

        return date_obj_naive


def trip_confirmation(request):
    """ A view to confirm booking request """

    template = "bookings/confirm/trip.html"
    context = {}

    if request.method == "POST":
        form = DateChoiceForm(request.POST)
        if form.is_valid():
            passengers = request.POST.get("num_passengers")
            trip_choice = request.POST.get("trip")

            context = {
                "passengers": passengers,
                "trip_choice": trip_choice
            }

            return render(request, template, context)


def booking_details(request):
    """ A view to collect all booking details needed for booking """

    context = {}
    template = ""
    return render(request, template, context)

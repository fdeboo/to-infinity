""" Views in this module provides logic for templates that guide
the booking process """

from datetime import datetime
from django.shortcuts import render
from .models import Trip
from .forms import DateChoiceForm, InitialSearchForm


def timezone_naive(queryset):
    """ Turns date atrribute to a time-zone naive date """

    date_attr = queryset.date
    date_string = date_attr.strftime("%Y-%m-%d")
    date_obj_naive = datetime.strptime(date_string, "%Y-%m-%d")

    return date_obj_naive


def initial_search(request):
    """ A view to show results of search """

    if request.method == "POST":
        postform = InitialSearchForm(request.POST)
        if postform.is_valid():
            destination_choice = request.POST.get("destination")
            searched_date = request.POST.get("request_date")
            passenger_total = request.POST.get("passengers")

            # Find trips with enough seats for requested no. of passengers
            available_trips = Trip.objects.filter(
                destination=destination_choice
            ).filter(seats_available__gte=passenger_total)

            # Retrieve the objects with dates closest to searched_date
            # limit to 3 pre-/post-
            post_date_closest = available_trips.filter(
                date__gte=searched_date
            ).order_by("date")[:3]
            prev_date_closest = available_trips.filter(
                date__lt=searched_date
            ).order_by("-date")[:3]

            # Merge both queries
            trips = post_date_closest | prev_date_closest

            # Find single object with closest date
            closest_gte = post_date_closest[0]
            closest_lt = prev_date_closest[0]

            # Parse all dates to same date type (naive) for operations
            naive_searched_date = datetime.strptime(searched_date, "%Y-%m-%d")
            naive_closest_gte = timezone_naive(closest_gte)
            naive_closest_lt = timezone_naive(closest_lt)

            if (
                naive_closest_gte - naive_searched_date >
                naive_searched_date - naive_closest_lt
            ):
                default_selected = closest_lt
            else:
                default_selected = closest_gte

            form = DateChoiceForm(
                trips=trips,
                initial={
                    'num_passengers': passenger_total,
                    'trip_date': default_selected.pk
                }
            )
            template = "bookings/availability.html"
            context = {"form": form}
            return render(request, template, context)

""" Views in this module provides logic for templates that guide
the booking process """

from django.shortcuts import render
from .models import Trip
from .forms import DateChoiceForm, InitialSearchForm


def initial_search(request):
    """ A view to show results of search """

    template = "bookings/availability.html"

    if request.method == 'POST':
        form = InitialSearchForm(request.POST)
        if form.is_valid():
            destination_choice = request.GET["destination"]
            searched_date = request.GET["request_date"]
            passenger_total = request.GET["passengers"]

            # Find trips with avaialabilty for requested no. of passengers
            available_trips = Trip.objects.filter(
                destination=destination_choice
            ).filter(seats_available__gte=passenger_total)

            # Retrieve the (max) 3 pre & post dates closest to searched date
            post_date_closest = available_trips.filter(
                date__gte=searched_date
            ).order_by("date")[:3]
            prev_date_closest = available_trips.filter(
                date__lt=searched_date
            ).order_by("-date")[:3]

            # Merge both queries
            trips = post_date_closest | prev_date_closest

            # Pass queryset to form instance
            form = DateChoiceForm(trips=trips)

    context = {
        "trips": trips,
        "form": form
    }

    return render(request, template, context)

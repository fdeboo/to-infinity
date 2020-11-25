""" Views in this module provides logic for templates that guide
the booking process """

from django.shortcuts import render
from .models import Trip


def initial_search(request):
    """ A view to show results of search """

    template = "bookings/availability.html"

    if request.GET:
        if "destination" in request.GET:
            destination_choice = request.GET["destination"]
            searched_date = request.GET["request_date"]
            passenger_total = request.GET["passengers"]
            trips = Trip.objects.filter(destination=destination_choice).filter(
                seats_available__gte=passenger_total
            )

            # Retrieve the (max) 3 pre & post dates closest to searched date
            post_date_closest = trips.filter(date__gte=searched_date).order_by(
                "date"
            )[:3]
            prev_date_closest = trips.filter(date__lt=searched_date).order_by(
                "-date"
            )[:3]

            # Merge both queries
            destinations = post_date_closest | prev_date_closest
    context = {"trips": destinations}
    return render(request, template, context)

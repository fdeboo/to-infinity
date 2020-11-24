from django.shortcuts import render
from .models import Trip
from .forms import InitialForm


def initial_search(request):
    """ A view to show all results of search """
    template = 'bookings/availability.html'
    initial_search = InitialForm(request)

    if request.GET:
        if 'destination' in request.GET:
            destination_choice = request.GET['destination']
            date_choice = request.GET['request_date']
            passenger_total = request.GET['passengers']
            trips = Trip.objects.filter(
                destination=destination_choice
            ).filter(
                seats_available__gte=passenger_total
            )
            print(destination_choice)  
            print(destinations)  
    context = {
        'trips': destinations
    }
    return render(request, template, context)

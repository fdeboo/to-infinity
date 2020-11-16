from django.shortcuts import render, get_object_or_404
from .models import Product


def all_trips(request):
    """ A view to show all trips """
    template = 'products/trips.html'
    trips = Product.objects.filter(category="destination")

    context = {
        "trips": trips,
    }

    return render(request, template, context)


def trip_detail(request, product_id):
    """ A view to show individual event details """
    trip = get_object_or_404(Product, pk=product_id)

    template = 'products/trip_detail.html'

    context = {
        "trip": trip,
    }

    return render(request, template, context)

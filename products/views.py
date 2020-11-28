"""
Provides logic and context for the all_trips trip_detail
"""
from django.shortcuts import render, get_object_or_404
from bookings.forms import InitialSearchForm
from .models import Product


def all_trips(request):
    """ A view to show all trips """

    template = 'products/trips.html'
    destinations = Product.objects.filter(category=3)
    intital_form = InitialSearchForm()

    context = {
        "destinations": destinations,
        "form": intital_form
    }

    return render(request, template, context)


def trip_detail(request, product_id):
    """ A view to show individual destination details """

    destination = get_object_or_404(Product, pk=product_id)

    template = 'products/trip_detail.html'
    context = {
        "destination": destination,
    }

    return render(request, template, context)

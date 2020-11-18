from django.shortcuts import render, get_object_or_404
from .models import Product


def all_trips(request):
    """ A view to show all trips """
    template = 'products/trips.html'
    destinations = Product.objects.filter(category=3)

    context = {
        "destinations": destinations,
    }

    return render(request, template, context)


def trip_detail(request, product_id):
    """ A view to show individual event details """
    destination = get_object_or_404(Product, pk=product_id)

    template = 'products/trip_detail.html'

    context = {
        "destination": destination,
    }

    return render(request, template, context)

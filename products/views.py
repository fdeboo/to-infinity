from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from .models import Product


def all_trips(request):
    """ A view to show all trips """
    template = 'products/trips.html'
    destinations = Product.objects.filter(category=3)

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!"
                    )
                return redirect(reverse('trips'))

            queries = Q(name__icontains=query) | Q(
                description__icontains=query
                )
            destinations = destinations.filter(queries)    

    context = {
        "destinations": destinations,
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

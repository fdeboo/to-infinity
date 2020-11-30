"""
Provides logic and context for the all_trips trip_detail
"""
from django.shortcuts import render, get_object_or_404
from django.views import View
from bookings.forms import InitialSearchForm
from .models import Product


class AllTrips(View):
    """ A view to show all trips and receive initial trip search """

    template = 'products/trips.html'
    form_class = InitialSearchForm

    def get(self, request):
        """ Renders the form to the template """

        destinations = Product.objects.filter(category=3)
        form = self.form_class()
        context = {
            "destinations": destinations,
            "form": form
        }
        return render(request, self.template, context)


def trip_detail(request, product_id):
    """ A view to show individual destination details """

    destination = get_object_or_404(Product, pk=product_id)

    template = 'products/trip_detail.html'
    context = {
        "destination": destination,
    }

    return render(request, template, context)

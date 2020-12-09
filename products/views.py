"""
Provides logic and context for the all_trips trip_detail
"""

from django.views.generic import DetailView, ListView
from bookings.forms import SearchTripsForm
from .models import Product, Destination


class DestinationListView(ListView):
    """ A view to show all trips and receive trip search data """

    model = Destination
    context_object_name = "destinations"
    template_name = "products/destinations/destination_list.html"

    def get_context_data(self, **kwargs):
        """ Add Search Trips form to the context """

        context = super().get_context_data(**kwargs)
        context['form'] = SearchTripsForm()
        return context


class DestinationDetailView(DetailView):
    """ A view to show individual destination details """

    model = Product
    template_name = "products/trip_detail.html"

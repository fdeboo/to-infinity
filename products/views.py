"""
Provides logic and context for the all_trips trip_detail
"""

import json
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.core.serializers.json import DjangoJSONEncoder
from bookings.forms import SearchTripsForm
from .models import Product, Destination


class DestinationListView(ListView):
    """ A view to handle the get request for template and show all trips """

    model = Destination
    template_name = "products/destination_list.html"
    context_object_name = 'destinations'

    def get_context_data(self, **kwargs):
        """ Add Search Trips form to the context """

        context = super(DestinationListView, self).get_context_data(**kwargs)
        context['form'] = SearchTripsForm()
        return context

    def post(self, request):
        """ Process the SearchTripForm and save input values to session """

        form = SearchTripsForm(self.request.POST)
        if form.is_valid():
            date = form.cleaned_data["request_date"]
            date = json.dumps(date, cls=DjangoJSONEncoder)
            self.request.session['request_date'] = date
            self.request.session["destination_choice"] = form.cleaned_data[
                "destination"].id
            self.request.session["passenger_total"] = form.cleaned_data[
                "passengers"]

            return HttpResponseRedirect(reverse("confirm_trip"))


class DestinationDetailView(DetailView):
    """ A view to show individual destination details """

    model = Product
    template_name = "products/destination_detail.html"

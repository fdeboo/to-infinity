"""
Provides logic and context for the all_trips trip_detail
"""

import json
from django.shortcuts import render, get_object_or_404, reverse
from django.views.generic.edit import FormView
from django.core.serializers.json import DjangoJSONEncoder
from bookings.forms import SearchTripsForm
from .models import Product


class TripsView(FormView):
    """ A view to show all trips and receive trip search data """

    template_name = "products/trips.html"
    form_class = SearchTripsForm

    def get_success_url(self):
        """ Overides the success url when the view is run """

        return reverse("selection")

    def get_context_data(self, **kwargs):
        """ Renders the form to the template """

        context = super().get_context_data(**kwargs)
        context["destinations"] = Product.objects.filter(category=3)
        return context

    def form_valid(self, form):
        """
        Takes the POST data from the SearchTripsForm and sends to the session
        """

        date = form.cleaned_data["request_date"]
        date = json.dumps(date, cls=DjangoJSONEncoder)
        self.request.session["searched_date"] = date
        self.request.session["destination_choice"] = form.cleaned_data[
            "destination"
        ].id
        self.request.session["passenger_total"] = form.cleaned_data[
            "passengers"
        ]
        return super(TripsView, self).form_valid(form)


def trip_detail(request, product_id):
    """ A view to show individual destination details """

    destination = get_object_or_404(Product, pk=product_id)

    template = "products/trip_detail.html"
    context = {
        "destination": destination,
    }

    return render(request, template, context)

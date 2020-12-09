"""
Views in this module provide logic for templates that guide the booking process
"""

from datetime import datetime
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.views import View
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Trip, Booking, BookingLineItem, Product
from .forms import DateChoiceForm, PassengerFormSet


@method_decorator(never_cache, name='dispatch')
class ConfirmTripView(FormView):
    """
    Provides the user a set of choice options based on their search input in
    the products.TripsView
    """

    model = Booking
    template_name = "bookings/trips_available.html"
    form_class = DateChoiceForm

    def convert_to_int(self, type_tuple):
        """ Converts tuple value to integer """

        type_int = int(''.join(type_tuple))
        return type_int

    def get_available_trips(self, destination, passengers):
        """ Find trips with enough seats for searched no. of passengers """

        available_trips = Trip.objects.filter(
            destination=destination
        ).filter(seats_available__gte=passengers)
        return available_trips

    def get_trips_matched_or_post_date(self, date, destination, passengers):
        """
        Returns trips that either match or are post- searched_date
        Refine to trips with dates closest to searched_date
        limit to 3 results
        """

        available_trips = self.get_available_trips(destination, passengers)
        gte_dates = available_trips.filter(date__gte=date)[:3]
        return gte_dates

    def get_trips_preceding_date(self, date, destination, passengers):
        """
        Returns trips that are pre- searched_date
        Refines to trips with dates closest to searched_date
        limits to 3 results
        """

        available_trips = self.get_available_trips(destination, passengers)
        lt_dates = available_trips.filter(date__lt=date).order_by("-date")[:3]
        return lt_dates

    def make_timezone_naive(self, obj):
        """ Turns date attribute to a time-zone naive date object """

        date_attr = obj.date
        date_string = date_attr.strftime("%Y-%m-%d")
        datetime_naive = datetime.strptime(date_string, "%Y-%m-%d")
        return datetime_naive

    def get_queryset(self, gte_dates, lt_dates):
        """ Creates the queryset that will be used by the ModelChoiceField
        in the DateChoiceForm """

        # Merge both queries
        trips = lt_dates | gte_dates
        trips = trips.order_by('date')
        return trips

    def get_context_data(self, **kwargs):
        """ Takes values from get request and formulates variables
        to be used in the form """

        # Values from GET request
        searched_date = self.request.GET.get('request_date')
        passengers = self.request.GET.get('passengers')
        destination_id = self.convert_to_int(
            self.request.GET.get("destination")
        )

        naive_searched_date = datetime.strptime(searched_date, "%Y-%m-%d")
        # Return querysets for dates before/beyond searched_date respectively:
        gte_dates = self.get_trips_matched_or_post_date(
            searched_date,
            destination_id,
            passengers)

        lt_dates = self.get_trips_preceding_date(
            searched_date,
            destination_id,
            passengers)

        destination = Product.objects.filter(id=destination_id)
        trips = self.get_queryset(gte_dates, lt_dates)

        # Find the trip closest to the searched_date (for form initial value)
        if gte_dates:
            gte_date = gte_dates[0]
            naive_gte_date = self.make_timezone_naive(gte_date)
            if lt_dates:
                lt_date = lt_dates[0]
                naive_lt_date = self.make_timezone_naive(lt_date)

                if (
                    naive_gte_date - naive_searched_date
                    > naive_searched_date - naive_lt_date
                ):
                    default_selected = lt_date
                else:
                    default_selected = gte_date

            else:
                default_selected = gte_date

        elif lt_dates:
            lt_date = lt_dates[0]
            default_selected = lt_date

        else:
            messages.error(
                self.request,
                "Sorry, there are no dates currently available for the"
                "selected destination.",
            )

        context = super().get_context_data(**kwargs)
        context["passengers"] = passengers
        context["destination_obj"] = destination
        context["default_selected"] = default_selected
        context["trips"] = trips
        return context

    def get_initial(self):
        """ Get initial valuees for the form """

        initial = super(ConfirmTripView, self).get_initial()
        context = self.get_context_data()
        default_selected = context["default_selected"]
        initial.update({'trip': default_selected})
        return initial

    def get_form_kwargs(self):
        kwargs = super(ConfirmTripView, self).get_form_kwargs()
        context = self.get_context_data()
        trips = context["trips"]
        kwargs.update({'trips': trips})
        return kwargs
    
    def form_valid(self, form):
        """
        Takes the POST data from the DateChoiceForm and creates an
        Intitial Booking in the database
        """

        context = self.get_context_data()
        form = context["form"]
        booking = form.save(commit=False)
        booking.status = "RESERVED"
        booking.save()
        trip = form.cleaned_data['trip']
        destination = trip.destination
        booking_line_item = BookingLineItem(
            booking=booking,
            product=destination,
            quantity=self.request.GET.get("passengers")
        )
        booking_line_item.save()
        return redirect('create_passengers', booking.pk)


@method_decorator(login_required, name='dispatch')
class CreatePassengersView(SingleObjectMixin, FormView):
    """
    A view to update booking with passenger details based on number of
    passengers in search
    """

    model = Booking
    template_name = 'bookings/passenger_details.html'

    def get(self, request, *args, **kwargs):
        # The Booking being updated:
        self.object = self.get_object(queryset=Booking.objects.all())
        print(self.object)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # The Booking being updated:
        self.object = self.get_object(queryset=Booking.objects.all())
        print(self.object)
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """ Use custom formset """

        return PassengerFormSet(
            **self.get_form_kwargs(),
            instance=self.object
        )

    def form_valid(self, form):
        """ If the form is valid, redirect to the supplied URL"""

        form.save()

        messages.add_message(
            self.request, messages.SUCCESS,
            'Changes were saved.'
        )

    def get_success_url(self):
        return reverse("complete_booking")


class CompleteBookingView(View):
    template = 'checkout.html'
    print('HERE')

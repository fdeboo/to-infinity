"""
Views in this module provide logic for templates that guide the booking process
"""

from datetime import datetime
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.views import View
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.cache import never_cache
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from profiles.models import UserProfile
from .models import Trip, Passenger, Booking, BookingLineItem, Product
from .forms import DateChoiceForm, PassengerForm, PassengerFormSet


@method_decorator(never_cache, name='dispatch')
class ConfirmTripView(View):
    """
    Provides the user a set of choice options based on their search input in
    the products.TripsView
    """

    template_name = "bookings/trips_available.html"
    form_class = DateChoiceForm

    def convert_to_int(self, type_tuple):
        """ Converts tuple value to integer """

        type_int = int(''.join(type_tuple))
        print(type_int)
        return type_int

    def get_available_trips(self, destination, passengers):
        """ Find trips with enough seats for searched no. of passengers """

        available_trips = Trip.objects.filter(
            destination=destination
        ).filter(seats_available__gte=passengers)
        return available_trips

    def get_trips_matched_or_post_date(self, date):
        """
        Returns trips that either match or are post- searched_date
        Refine to trips with dates closest to searched_date
        limit to 3 results
        """
        destination_id = self.convert_to_int(
            self.request.GET.get("destination")
        )
        available_trips = self.get_available_trips(
            destination_id,
            self.request.GET.get("passengers")
        )
        gte_dates = available_trips.filter(date__gte=date)[:3]
        return gte_dates

    def get_trips_preceding_date(self, date):
        """
        Returns trips that are pre- searched_date
        Refines to trips with dates closest to searched_date
        limits to 3 results
        """
        destination_id = self.convert_to_int(
            self.request.GET.get("destination")
        )
        available_trips = self.get_available_trips(
            destination_id,
            self.request.GET.get("passengers")
        )
        lt_dates = available_trips.filter(date__lt=date).order_by("-date")[:3]
        return lt_dates

    def make_timezone_naive(self, obj):
        """ Turns date attribute to a time-zone naive date object """

        date_attr = obj.date
        date_string = date_attr.strftime("%Y-%m-%d")
        datetime_naive = datetime.strptime(date_string, "%Y-%m-%d")
        return datetime_naive

    def get_queryset(self):
        """ Creates the queryset that will be used by the ModelChoiceField
        in the DateChoiceForm """

        searched_date = self.request.GET.get('request_date')
        gte_dates = self.get_trips_matched_or_post_date(searched_date)
        lt_dates = self.get_trips_preceding_date(searched_date)
        # Merge both queries
        trips = lt_dates | gte_dates
        trips = trips.order_by('date')
        return trips

    def post(self, request):
        """
        Takes the POST data from the DateChoiceForm and creates an
        Intitial Booking in the database
        """

        trips = self.get_queryset()
        form = self.form_class(request.POST, trips=trips)
        if form.is_valid():
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
            print(booking.pk)

            return redirect('create_passengers', booking.pk)

    def get(self, request):
        """
        Initialises the DateChoiceForm with data from SearchTripsForm
        & renders to the template
        """

        searched_date = self.request.GET.get('request_date')
        naive_searched_date = datetime.strptime(searched_date, "%Y-%m-%d")
        gte_dates = self.get_trips_matched_or_post_date(searched_date)
        lt_dates = self.get_trips_preceding_date(searched_date)

        # Find the trip closest to searched_date and make timezone naive
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
                request,
                "Sorry, there are no dates currently available for the"
                "selected destination.",
            )

        trips = self.get_queryset()
        passengers = self.request.GET.get("passengers")
        destination_id = self.convert_to_int(
            self.request.GET.get("destination")
        )
        destination = Product.objects.filter(id=destination_id)
        form = self.form_class(
            trips=trips,
            initial={"trip": default_selected}
        )
        context = {
            "form": form,
            "passengers": passengers,
            "destination_obj": destination,
        }
        return render(request, self.template_name, context)


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

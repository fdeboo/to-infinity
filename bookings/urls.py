""" Defines the urls for bookings app including trips """

from django.urls import path
from bookings.views import TripSelection
from . import views


urlpatterns = [
    path("trips/", TripSelection.as_view(), name="selection"),
    path("confirm/", views.trip_confirmation, name="confirm"),
    path("details/", views.booking_details, name="booking_details"),
]

""" Defines the urls for bookings app including trips """

from django.urls import path
from bookings.views import SelectTripView, ConfirmTripView, CreateBookingView


urlpatterns = [
    path("trips/", SelectTripView.as_view(), name="selection"),
    path("confirm/", ConfirmTripView.as_view(), name="booking_details"),
    path("details/", CreateBookingView.as_view(), name="confirm"),
]

""" Defines the urls for bookings app including trips """

from django.urls import path
from bookings.views import SelectTripView, UpdateBookingView


urlpatterns = [
    path('trips/', SelectTripView.as_view(), name="selection"),
    path('details/<pk>', UpdateBookingView.as_view(), name="confirm"),
]

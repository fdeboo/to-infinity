""" Defines the urls for bookings app including trips """

from django.urls import path
from bookings.views import SelectTripView, ConfirmTripView
from . import views


urlpatterns = [
    path("trips/", SelectTripView.as_view(), name="selection"),
    path("confirm/", ConfirmTripView.as_view(), name="confirm"),
    path("details/", views.booking_details, name="booking_details"),
]

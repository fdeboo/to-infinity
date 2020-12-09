""" Defines the urls for bookings app including trips """

from django.urls import path
from . import views


urlpatterns = [
    path(
        'confirm/',
        views.ConfirmTripView.as_view(),
        name="confirm_trip"),

    path(
        '<pk>/passengers/add',
        views.CreatePassengersView.as_view(),
        name="create_passengers"),

    path(
        '<pk>/checkout/',
        views.CompleteBookingView.as_view(),
        name="complete_booking"),
]

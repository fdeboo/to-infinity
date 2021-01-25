""" Defines the urls for bookings app including trips """

from django.urls import path
from . import views


urlpatterns = [
    path(
        'search/',
        views.SearchTripsView.as_view(),
        name="search_trip"),

    path(
        'search/confirm/',
        views.ConfirmTripView.as_view(),
        name="confirm_trip"),

    path(
        'passengers/add/',
        views.InputPassengersView.as_view(),
        name="create_passengers"),

    path(
        '<pk>/cancel/',
        views.CancelBookingView.as_view(),
        name="cancel_booking"),

    path(
        '<pk>/edit/',
        views.EditBookingView.as_view(),
        name="edit_booking"),
]

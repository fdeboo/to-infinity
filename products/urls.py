""" Defines the urls for bookings app including trips """

from django.urls import path
from products.views import DestinationListView, DestinationDetailView


urlpatterns = [
    path(
        'destinations/',
        DestinationListView.as_view(),
        name='trips'),

    path(
        "destinations/<int:pk>/",
        DestinationDetailView.as_view(),
        name="trip_detail"),
]

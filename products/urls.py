""" Defines the urls for bookings app including trips """

from django.urls import path
from products.views import TripsView, TripDetail


urlpatterns = [
    path('trips/', TripsView.as_view(), name='trips'),
    path("trips/<pk>/", TripDetail.as_view(), name="trip_detail"),
]

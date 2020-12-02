""" Defines the urls for bookings app including trips """

from django.urls import path
from products.views import TripsView
from . import views


urlpatterns = [
    path('trips', TripsView.as_view(), name='trips'),
    path("trips/<int:product_id>/", views.trip_detail, name="trip_detail"),
]

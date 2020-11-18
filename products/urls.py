from django.urls import path
from . import views

urlpatterns = [
    path('trips', views.all_trips, name='trips'),
    path("trips/<int:product_id>/", views.trip_detail, name="trip_detail"),
]

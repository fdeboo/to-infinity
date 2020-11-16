from django.urls import path
from . import views

urlpatterns = [
    path('trips', views.all_trips, name='trips'),
]

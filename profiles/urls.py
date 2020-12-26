""" Defines the urls for bookings app including trips """

from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.ProfileView.as_view(),
        name='profile'),
]

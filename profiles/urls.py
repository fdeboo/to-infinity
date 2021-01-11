""" Defines the urls for profiles app including ProfileView """

from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.ProfileView.as_view(),
        name="profile"),
]

from django.urls import path
from . import views

urlpatterns = [
    path("stepone/", views.initial_search, name="initial_search"),
]

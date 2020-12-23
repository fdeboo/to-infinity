""" Defines the urls for checkout app """

from django.urls import path
from . import views
from .webhooks import webhook


urlpatterns = [
    path(
        'booking/<pk>/',
        views.CompleteBookingView.as_view(),
        name="complete_booking"),

    path(
        'success/booking/<pk>/',
        views.CheckoutSuccessView.as_view(),
        name="checkout_success"),

    path('wh/', webhook, name='webhook'),

    path(
        "cache_checkout_data/",
        views.cache_checkout_data,
        name="cache_checkout_data",
    ),
]

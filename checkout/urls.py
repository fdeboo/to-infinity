""" Defines the urls for checkout app """

from django.urls import path
from . import views


urlpatterns = [
    path(
        'booking/<pk>/',
        views.CreateOrderView.as_view(),
        name="create_order"),

    path(
        'success/booking/<pk>/',
        views.CheckoutSuccessView.as_view(),
        name="checkout_success"),

]

from django.contrib import admin
from .models import Booking, BookingLineItem, Passenger, Trip


class BookingLineItemAdminInline(admin.TabularInline):
    model = BookingLineItem
    readonly_fields = ("line_total",)


class PassengerAdminInline(admin.TabularInline):
    model = Passenger


class BookingAdmin(admin.ModelAdmin):
    inlines = (BookingLineItemAdminInline, PassengerAdminInline)

    """ Can view but not edit the following """
    readonly_fields = (
        "booking_ref",
        "booking_total",
        "stripe_pid",
        "trip",
        "status",
    )

    fields = (
        "booking_ref",
        "booking_total",
        "stripe_pid",
        "trip",
        "status",
    )

    """ Fields displayed in add or change """
    list_display = (
        "booking_ref",
        "booking_total",
    )


class TripAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'destination',
        'seats_available',
    )

    ordering = (
        'date',
    )


admin.site.register(Booking, BookingAdmin)
admin.site.register(Trip, TripAdmin)

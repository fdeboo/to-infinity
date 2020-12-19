from django.contrib import admin
from .models import Booking, BookingLineItem, Passenger, Trip


class BookingLineItemAdminInline(admin.TabularInline):
    model = BookingLineItem
    readonly_fields = ("line_total", "product", "quantity")


class PassengerAdminInline(admin.TabularInline):
    model = Passenger


class BookingAdmin(admin.ModelAdmin):
    inlines = (BookingLineItemAdminInline, PassengerAdminInline)

    """ Can view but not edit the following """
    readonly_fields = (
        "id",
        "booking_ref",
        "booking_total",
        "stripe_pid",
        "trip",
        "status",
    )

    fields = (
        "id",
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
    readonly_fields = (
        "trip_ref",
    )

    list_display = (
        "trip_ref",
        "date_display",
        "destination",
        "seats_available",
    )

    ordering = ("date",)

    def date_display(self, obj):
        return obj.date.strftime("%Y %b %d %H:%M:%S")

    date_display.admin_order_field = "date"
    date_display.short_description = "Precise Time"


admin.site.register(Booking, BookingAdmin)
admin.site.register(Trip, TripAdmin)

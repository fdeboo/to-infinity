from django.contrib import admin
from .models import Booking, BookingLineItem, Passenger


class BookingLineItemAdminInline(admin.TabularInline):
    model = BookingLineItem
    readonly_fields = ("line_total",)


class PassengerAdminInline(admin.TabularInline):
    model = Passenger
    readonly_fields = ("medical_assessment",)


class BookingAdmin(admin.ModelAdmin):
    inlines = (BookingLineItemAdminInline, PassengerAdminInline)

    """ Can view but not edit the following """
    readonly_fields = (
        "booking_ref",
        "date",
        "booking_total",
        "stripe_pid",
    )

    fields = (
        "booking_ref",
        "user_profile",
        "first_name",
        "email",
        "booking_total",
        "stripe_pid",
    )

    """ Fields displayed in add or change """
    list_display = (
        "booking_ref",
        "first_name",
        "booking_total",
    )

    ordering = ("-date",)


admin.site.register(Booking, BookingAdmin)

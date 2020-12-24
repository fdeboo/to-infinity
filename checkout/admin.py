from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ("line_total", "product", "quantity")


class OrderAdminInline(admin.TabularInline):
    model = Order
    readonly_fields = (
        "Order_total",
        "status",
    )


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    """ Can view but not edit the following """
    readonly_fields = (
        "id",
        "order_total",
    )

    fields = (
        "id",
        "full_name",
        "email",
        "phone_number",
        "street_address1",
        "street_address2",
        "town_or_city",
        "postcode",
        "country",
        "county",
        "order_total",
    )

    """ Fields displayed in add or change """
    list_display = (
        "order_total",
    )


admin.site.register(Order, OrderAdmin)

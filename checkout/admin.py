from django.contrib import admin
from .models import Billing


class BillingAdmin(admin.ModelAdmin):


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
        "full_name",
        "email",
    )


admin.site.register(Billing,)

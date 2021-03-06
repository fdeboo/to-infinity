from django.contrib import admin
from .models import Product, Category, AddOn, Insurance, Destination


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_id',
        'name',
        'category',
        'price',
        'image',
    )

    ordering = (
        'product_id',
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )


class AddOnAdmin(ProductAdmin):
    list_display = (
        'product_id',
        'name',
        'category',
        'price',
        'image',
        'min_medical_threshold',
    )

    readonly_fields = (
        'category',
    )

    ordering = (
        'product_id',
    )


class InsuranceAdmin(ProductAdmin):
    list_display = (
        'product_id',
        'name',
        'category',
        'price',
        'image',
        'friendly_name',
    )

    readonly_fields = (
        'category',
    )

    ordering = (
        'product_id',
    )


class DestinationAdmin(ProductAdmin):
    list_display = (
        'product_id',
        'name',
        'max_passengers',
        'duration',
        'min_medical_threshold',
        'category',
        'price',
        'image',
    )

    readonly_fields = (
        'category',
    )

    ordering = (
        'product_id',
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(AddOn, AddOnAdmin)
admin.site.register(Insurance, InsuranceAdmin)
admin.site.register(Destination, DestinationAdmin)

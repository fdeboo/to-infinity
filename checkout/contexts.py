"""
Logic that enables the booking summary to updated from the template.
"""
from django.shortcuts import get_object_or_404
from products.models import Product


def booking_summary(request):
    """ Retrieves items from the session and updates accordingly """

    booking_items = []
    addon_items = []
    trip_items = []
    total = 0
    product_count = 0
    items = request.session.get('booking_items', {})

    for product_id, quantity in items.items():
        product = get_object_or_404(Product, pk=product_id)
        item = {
            'product': product,
            'quantity': quantity,
            'line_total': (product.price * quantity)
        }
        total += item['line_total']
        product_count += quantity
        booking_items.append(item)
        if product.category.pk == 1:
            addon_items.append(item)
        elif product.category.pk == 3:
            trip_items.append(item)
        else:
            pass

    context = {
        'booking_items': booking_items,
        'addon_items': addon_items,
        'total': total,
        'product_count': product_count,
    }

    return context

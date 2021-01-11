"""
Provides logic to render the user profile page. Handles the form input to \
update profile information
"""
import ast
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from bookings.models import Booking
from products.models import Product
from .models import UserProfile
from .forms import UserProfileForm


@method_decorator(login_required, name="dispatch")
class ProfileView(UpdateView):
    """ A view that renders a user's profile information and order history """

    model = UserProfile
    template_name = 'profiles/profile.html'
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        """ Gets relevant profile using the current user """
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        """ Adds to the users current bookings context dictionary """

        user = self.get_object()
        #  Find any complete or incomplete bookings that the user has made
        editable_bookings = Booking.objects.filter(
            lead_passenger=user).filter(status='OPENED')
        complete_bookings = Booking.objects.filter(
            lead_passenger=user).filter(status='COMPLETE')

        # Provide the context for the booking summary
        open_bookings = []
        for booking in editable_bookings.values():
            if booking['original_bag'] != "":
                booking_items = []
                original_bag = booking['original_bag']
                items = ast.literal_eval(original_bag)

                for product_id, quantity in items.items():
                    product = Product.objects.get(pk=product_id)
                    booking_item = {
                        "product": product,
                        "quantity": quantity,
                        "line_total": product.price * quantity,
                    }
                    booking_items.append(booking_item)
                    booking['booking_items'] = booking_items
                    booking['booking_total'] += booking_item['line_total']
                    open_bookings.append(booking)

            else:
                pass

        context = super().get_context_data(**kwargs)
        context["open_bookings"] = open_bookings
        context["complete_bookings"] = complete_bookings
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully')

    def form_invalid(self, form):
        messages.error(
                self.request, 'Update failed. Please ensure the form is valid'
            )

"""
Defines the form objects to be used for the booking aspects of the app
Includes a form to search available dates
"""

from django import forms
from django_countries.fields import CountryField
# from .models import Billing


class BookingPaymentForm(forms.Form):
    """ Form to collect payment information for billing """

    full_name = forms.CharField(required=True, max_length=50)
    email = forms.EmailField(required=True, max_length=100)
    phone_number = forms.CharField(required=True, max_length=20)
    postcode = forms.CharField(required=True, max_length=20)
    town_or_city = forms.CharField(required=True, max_length=40)
    street_address1 = forms.CharField(required=True, max_length=80)
    street_address2 = forms.CharField(required=False, max_length=80)
    county = forms.CharField(required=False, max_length=80)
    country = CountryField(blank_label="Country *").formfield()

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            "full_name": "Full Name",
            "email": "Email Address",
            "phone_number": "Phone Number",
            "postcode": "Postal Code",
            "town_or_city": "Town or City",
            "street_address1": "Street Address 1",
            "street_address2": "Street Address 2",
            "county": "County, State or Locality",
        }

        self.fields["full_name"].widget.attrs["autofocus"] = True
        for field in self.fields:
            if field != "country":
                if self.fields[field].required:
                    placeholder = f"{placeholders[field]} *"
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs["placeholder"] = placeholder
            self.fields[field].widget.attrs["class"] = "stripe-style-input"
            self.fields[field].label = False

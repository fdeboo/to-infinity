"""
Defines the form objects to be used for the booking aspects of the app
Includes a form to search available dates
"""
from django import forms
from django_countries.fields import CountryField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Field,
    Fieldset,
    Div,
    HTML,
    Hidden,
)
from bookings.models import Booking


class CustomCheckbox(Field):
    """ Provides template for custom Checkbox field used in crispy form """
    template = 'checkout/forms/saveinfo-checkbox.html'


class BookingCheckoutForm(forms.ModelForm):
    """ Form to collect payment information for billing """

    class Meta:
        model = Booking
        fields = ["full_name", "contact_number", "contact_email"]

    saveinfo = forms.BooleanField(required=False)
    street_address1 = forms.CharField(required=True, max_length=80)
    street_address2 = forms.CharField(required=False, max_length=80)
    town_or_city = forms.CharField(required=True, max_length=40)
    county = forms.CharField(required=False, max_length=80)
    postcode = forms.CharField(required=True, max_length=20)
    country = CountryField(blank_label="Country *").formfield()

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs["autofocus"] = True
        for field in self.fields:
            if field != "saveinfo":
                self.fields[field].widget.attrs["class"] = "all-form-input"
                self.fields[field].label = False
            else:
                self.fields[field].label = "Save this number to my profile"

        # Defines the layout for the form using crispy FormHelper
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_class = "crispyform"
        self.helper.form_id = "payment-form"
        self.helper.layout = Layout(
            HTML(
                """
                <div class="row">
                    <div class="col-12 col-lg-6">
                        <p class="booking-subheader">Please fill out the \
                            form below to complete your booking
                        </p>
                        <div class="crispyform">
                """
            ),
            Fieldset(
                "Contact Details",
                Field("full_name", placeholder="Full Name", autofocus=True),
                Field("contact_email", placeholder="Email Address"),
                Field("contact_number", placeholder="Phone Number"),
                CustomCheckbox('saveinfo'),
                css_class="rounded px-3 mb-3",
            ),
            Fieldset(
                "Billing Details",
                Field("street_address1", placeholder="Street Address 1 *"),
                Field("street_address2", placeholder="Street Address 2"),
                Field("town_or_city", placeholder="Town or City *"),
                Field("county", placeholder="County, State or Locality"),
                Field("postcode", placeholder="Postal Code *"),
                Field("country", placeholder="Country *"),
                css_class="rounded px-3 mb-3",
            ),
            Fieldset(
                "Payment",
                Div(css_class="mb-3 all-form-input", id="card-element"),
                Div(
                    css_class="text-danger mb-3",
                    id="card-errors",
                    role="alert"
                    ),
                Hidden(
                    css_class="text-danger mb-3",
                    value="{{ client_secret }}",
                    name="client_secret"
                    ),
                css_class="px-3",
            ),
            HTML(
                """
                    </div>
                </div>

                {% include 'checkout/includes/summary/checkout-summary.html' %}
                """
            )
        )

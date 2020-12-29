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
    ButtonHolder,
)


class CustomCheckbox(Field):
    """ Provides template for custom Checkbox field used in crispy form """
    template = 'checkout/forms/saveinfo-checkbox.html'


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
    saveinfo = forms.BooleanField(required=False)

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
        self.helper.form_id = "payment-form"
        self.helper.layout = Layout(
            Fieldset(
                "Contact Details",
                Field("full_name", placeholder="Full Name", autofocus=True),
                Field("email", placeholder="Email Address"),
                Field("phone_number", placeholder="Phone Number"),
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
            ButtonHolder(
                HTML(
                    """
                    <a href="#" class="btn btn-outline rounded-0">
                        <span class="icon">
                            <i class="fas fa-chevron-left"></i>
                        </span>
                        <span class="font-weight-bold">Adjust Booking</span>
                    </a>
                    """
                ),
                HTML(
                    """
                    <button id="submit-button" class="btn btn-outline \
                        rounded-0">
                        <span class="font-weight-bold">Complete Order</span>
                        <span class="icon">
                            <i class="fas fa-lock"></i>
                        </span>
                    </button>
                    """
                ),
                css_class="submit-button text-right px-3 mt-3 mb-2",
            ),
        )

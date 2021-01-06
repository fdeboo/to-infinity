"""
Defines the form objects to be used for the booking aspects of the app
Includes a form to search available dates
"""
import re
from datetime import date
from django import forms
from django.forms.widgets import Select
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Submit,
    Field,
    Div,
    ButtonHolder,
)
from products.models import AddOn
from .models import Destination, Booking, Passenger
from .formset import Formset


class DateInput(forms.DateInput):
    """
    Override the default input type for Django's DateInput Widget
    as suggested here: https://www.youtube.com/watch?v=I2-JYxnSiB0.
    Renders <input type="date"> in html
    """

    input_type = "date"


class SelectOptionsWithAttributes(Select):
    """
    Creates a custom widget that sublasses Django's select widget.
    Customises it's create_option method
    Allows attributes to be added the option elements of the Select

    Since the options of a Select widget are list of tuples containing
    the value and label ie. [('value_1, 'label_1')],

    Pass a dictionary instead of string for it's label:
    ie. [('value_1, {'label': 'label_1', 'foo': 'bar', ...})]

    The extra key/values in the dictionary render as HTML attributes

    Code and explanation courtesy this StackOverflow post:
    https://stackoverflow.com/questions/38944814/how-to-add-data-attribute-to-django-modelform-modelchoicefield
    """

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        if isinstance(label, dict):
            opt_attrs = label.copy()
            label = opt_attrs.pop("label")
        else:
            opt_attrs = {}
        option_dict = super(SelectOptionsWithAttributes, self).create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        for key, val in opt_attrs.items():
            option_dict["attrs"][key] = val
        return option_dict


class DestinationChoiceField(forms.ModelChoiceField):
    """
    Overrides the label_from_instance method from Django's ModelChoiceField:
    Passes the 'max_passengers' value from the object as an html5
    data-attribute
    """

    widget = SelectOptionsWithAttributes

    def label_from_instance(self, obj):
        # 'obj' will be a Destination
        return {
            # the usual label:
            "label": super().label_from_instance(obj),
            # the new data attribute:
            "data-max-num": obj.max_passengers,
        }


class TripChoiceField(forms.ModelChoiceField):
    """
    Overrides the label_from_instance method from Django's ModelChoiceField:
    Overwrites the display text
    """

    def label_from_instance(self, obj):
        # 'obj' will be a Destination
        date_string = (obj.date).strftime("%A %d %B %Y")
        return f"{date_string} £{obj.destination.price}"


class SearchTripsForm(forms.Form):
    """
    Provides a list of deestination options and inputs for no. of passengers
    and date preference.
    All fields include an id attribute for referencing in Javascript
    """

    destination = DestinationChoiceField(
        queryset=Destination.objects.all(),
        label="",
        empty_label="Destination",
        widget=SelectOptionsWithAttributes(),
    )
    request_date = forms.DateField(required=True, label="", widget=DateInput())
    passengers = forms.IntegerField(label="", widget=forms.NumberInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_class = "d-flex"
        self.helper.field_class = "col-12"
        self.helper.layout = Layout(
            Field(
                "destination",
                wrapper_class="mb-0 d-flex align-items-center",
                css_class="form-control-lg mb-3 all-form-input",
                id="selected-trip",
            ),
            Field(
                "request_date",
                min=date.today(),
                max="2040-12-20",
                wrapper_class="mb-0 d-flex align-items-center",
                css_class="form-control-lg mb-3 all-form-input",
            ),
            Field(
                "passengers",
                min="1",
                disabled="true",
                id="passengers-max",
                placeholder="No. of Passengers",
                wrapper_class="mb-0 d-flex align-items-center",
                css_class="form-control-lg mb-3 all-form-input",
            ),
            ButtonHolder(
                Submit("submit", "Search", css_class="btn btn-outline"),
                css_class="ml-lg-auto col-12 col-lg-auto text-right",
            ),
        )

    def clean(self):
        """ Form validation in case bad data passes validation in browser """

        # Data from the form is fetched using super function
        super(SearchTripsForm, self).clean()

        # Extract the individual fields from the data
        destination = self.cleaned_data.get("destination")
        request_date = self.cleaned_data.get("request_date")
        passengers = self.cleaned_data.get("passengers")

        if not isinstance(destination, Destination):
            self._errors["destimation"] = self.error_class(
                ["Please choose an option from the list"]
            )

        elif passengers > destination.max_passengers:
            self._errors["passengers"] = self.error_class(
                ["Sorry, this exceeds the maximum for selected trip"]
            )

        elif passengers < 0:
            self._errors["passengers"] = self.error_class(
                ["Please choose at least one passenger"]
            )

        if request_date < date.today():
            self._errors["request_date"] = self.error_class(
                ["Searched date should not be in the past"]
            )

        # return any errors if found
        return self.cleaned_data


class DateChoiceForm(forms.ModelForm):
    """
    Provides user a choice of available dates relative to their preference.
    Uses 'radio' type input which allows only one option to be selected.
    By default the closest date to the users searched date is selected.
    """

    class Meta:
        model = Booking
        fields = ["trip"]
        field_classes = {"trip": TripChoiceField}
        widgets = {"trip": forms.RadioSelect()}

    def __init__(self, *args, **kwargs):
        trip_dates = kwargs.pop("trips", None)
        super(DateChoiceForm, self).__init__(*args, **kwargs)
        self.fields["trip"].queryset = trip_dates


class CustomCheckbox(forms.CheckboxSelectMultiple):
    """
    Creates a custom checkbox select widget that subclasses Django's
    CheckboxSelectMultiple and customises it with a different template
    """

    template_name = 'bookings/forms/checkbox_select.html'
    option_template_name = 'bookings/forms/checkbox_option.html'

    def create_option(
        self, name, value, label, selected, index, subindex, attrs
    ):
        obj = AddOn.objects.get(pk=value)
        option_dict = super(CustomCheckbox, self).create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        option_dict['template_name'] = self.option_template_name
        option_dict['object'] = obj

        return option_dict


def make_passenger_form(active_booking):
    """
    Provides the PassengerForm with the booking instance received in params
    (used to create queryset for addon field, and to validate each individual
    form instance.
    """

    class PassengerForm(forms.ModelForm):
        """
        Defines the form used in the PassengerFormset and validates each form
        individually
        """

        class Meta:
            model = Passenger
            fields = (
                "first_name",
                "last_name",
                "email",
                "passport_no",
                "trip_addons",
            )
            widgets = {
                "trip_addons": CustomCheckbox(),
                "is_leaduser": forms.HiddenInput(),
            }

        def __init__(self, *args, **kwargs):
            super(PassengerForm, self).__init__(*args, **kwargs)

            # Uses value from function param to create query for qs.
            self.fields["trip_addons"].queryset = AddOn.objects.filter(
                destination=active_booking.trip.destination
            )
            formtag_prefix = re.sub("-[0-9]+$", "", kwargs.get("prefix", ""))
            self.helper = FormHelper()
            self.helper.form_tag = False
            self.helper.form_error_title = "Form Errors"
            self.helper.formset_error_title = "Formset Errors"
            for field in self.fields:
                if field != "trip_addons":
                    self.fields[field].widget.attrs["class"] = "form-control-lg \
                        mt-0 all-form-input"
                    self.fields[field].label = False

            # CSS classes added to form elements
            self.helper.layout = Layout(
                Div(
                    Field(
                        "first_name",
                        placeholder="Full Name",
                    ),
                    Field(
                        "last_name",
                        placeholder="Last Name",
                    ),
                    Field(
                        "email",
                        placeholder="Email Address",
                    ),
                    Field(
                        "passport_no",
                        placeholder="Passport Number",
                    ),
                    Field(
                        "trip_addons",
                        template="bookings/forms/add-checkbox-custom.html",
                    ),

                    css_class="formset_row-{}".format(formtag_prefix),
                ),
            )

        def clean(self):
            """ Validation for fields in each individual form """

            # Data from the form fetched using super function
            super(PassengerForm, self).clean()

            # Collect data from field
            passport_no = self.cleaned_data.get("passport_no")
            if passport_no is None:
                self._errors["passport_no"] = self.error_class(
                    ["This field is required."]
                )

            else:
                # Validate if passenger already exists on any bookings
                # for the same trip
                existing_passengers = Passenger.objects.filter(
                    booking__trip=active_booking.trip
                ).filter(
                    booking__trip__bookings__passengers__passport_no=passport_no
                )
                if existing_passengers:
                    self._errors["passport_no"] = self.error_class(
                        ["Error, please check passport number or contact us"]
                    )

    return PassengerForm


class InputPassengersForm(forms.ModelForm):
    """Defines the overall form within which the PassengerFormset is nested."""

    class Meta:
        model = Booking
        fields = ("trip",)
        widgets = {"trip": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(InputPassengersForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.label_class = "col-md-3 create-label"
        self.helper.field_class = "col-md-12"
        self.helper.layout = Layout(
            Div(
                Field("trip"),
                # Custom layout object defined externally
                Formset("passenger_formset"),
            ),
            ButtonHolder(
                Submit("submit", "Proceed", css_class="m-0 btn btn-outline"),
            ),
        )

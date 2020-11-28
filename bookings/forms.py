"""
Defines the form objects to be used for the booking aspects of the app
Includes a form to search available dates
"""
from datetime import date
from django import forms
from django.forms import ModelChoiceField, NumberInput
from django.forms.widgets import Select
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, ButtonHolder
from .models import Destination


class DateInput(forms.DateInput):
    """
    Override the default input type for Django's DateInput Widget
    as suggested here: https://www.youtube.com/watch?v=I2-JYxnSiB0.
    Renders <input type="date"> in html
    """

    input_type = "date"


class SelectWithOptionAttribute(Select):
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
        option_dict = super(SelectWithOptionAttribute, self).create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        for key, val in opt_attrs.items():
            option_dict["attrs"][key] = val
        return option_dict


class DestinationChoiceField(ModelChoiceField):
    """
    Subclasses Django's ModelChoiceField and customises it's
    label_from_instance method to include 'max_passengers' from
    the queryset as an data-attribute in the html element
    """

    widget = SelectWithOptionAttribute

    def label_from_instance(self, obj):
        # 'obj' will be a Destination
        return {
            # the usual label:
            "label": super().label_from_instance(obj),
            # the new data attribute:
            "data-max-num": obj.max_passengers,
        }


class InitialSearchForm(forms.Form):
    """
    Collects user's desired deestination, no. of passengers and date preference
    Fields include an id attribute for referencing in Javascript
    """

    destination = DestinationChoiceField(
        queryset=Destination.objects.all(),
        label="",
        empty_label="Destination",
        widget=SelectWithOptionAttribute()
    )
    request_date = forms.DateField(
        required=True,
        label="",
        widget=DateInput()
    )
    passengers = forms.IntegerField(label="", widget=NumberInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = "initial_search"
        self.helper.form_class = "d-flex flex-column flex-lg-row"
        self.helper.field_class = 'col-12'
        self.helper.layout = Layout(
                Field(
                    "destination",
                    wrapper_class="mb-0 d-flex align-items-center",
                    css_class="form-control mb-3 mb-lg-0",
                    id="selected-trip",
                ),
                Field(
                    "request_date",
                    min=date.today(),
                    max="2040-12-20",
                    wrapper_class="mb-0 d-flex align-items-center",
                    css_class="form-control mb-3 mb-lg-0"
                ),
                Field(
                    "passengers",
                    min="1",
                    disabled="true",
                    id="passengers-max",
                    placeholder="No. of Passengers",
                    wrapper_class="mb-0 d-flex align-items-center",
                    css_class="form-control mb-3 mb-lg-0"
                ),
                ButtonHolder(
                    Submit(
                        "submit", "Search", css_class="btn btn-outline"
                    ), css_class="ml-lg-auto col-12 col-lg-auto text-right"
                )
            )


class DateChoiceForm(forms.Form):
    """
    Provides user with a choices of available dates beased on their preference.
    Uses input type, 'radio' and allows the user to select only one option.
    By default the closest date to the searched date is selected.
    """

    num_passengers = forms.IntegerField(widget=forms.HiddenInput())
    trip_date = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect()
    )

    def __init__(self, *args, **kwargs):
        trip_dates = kwargs.pop('trips', None)

        super(DateChoiceForm, self).__init__(*args, **kwargs)
        if trip_dates:
            self.fields['trip_date'].queryset = trip_dates

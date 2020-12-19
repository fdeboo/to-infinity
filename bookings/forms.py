"""
Defines the form objects to be used for the booking aspects of the app
Includes a form to search available dates
"""
from datetime import date
from django import forms
from django.forms import (
    ModelChoiceField,
    NumberInput,
    RadioSelect,
    HiddenInput,
    ModelForm,
    BaseInlineFormSet,
)
from django.forms.widgets import Select
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Submit,
    Field,
    Fieldset,
    Div,
    ButtonHolder
)

from .custom_layout_object import Formset
from .models import Destination, Booking


class DateInput(forms.DateInput):
    """
    Override the default input type for Django's DateInput Widget
    as suggested here: https://www.youtube.com/watch?v=I2-JYxnSiB0.
    Renders <input type="date"> in html
    """

    input_type = "date"


class SelectWithOptionAttributes(Select):
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
        option_dict = super(SelectWithOptionAttributes, self).create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        for key, val in opt_attrs.items():
            option_dict["attrs"][key] = val
        return option_dict


class DestinationChoiceField(ModelChoiceField):
    """
    Overrides the label_from_instance method from Django's ModelChoiceField:
    Passes the 'max_passengers' value from the object as an html5
    data-attribute
    """

    widget = SelectWithOptionAttributes

    def label_from_instance(self, obj):
        # 'obj' will be a Destination
        return {
            # the usual label:
            "label": super().label_from_instance(obj),
            # the new data attribute:
            "data-max-num": obj.max_passengers,
        }


class TripChoiceField(ModelChoiceField):
    """
    Overrides the label_from_instance method from Django's ModelChoiceField:
    Overwrites the display tezt
    """

    def label_from_instance(self, obj):
        # 'obj' will be a Destination
        date_string = (obj.date).strftime("%A %d %B %Y")
        return f'{date_string} £{obj.destination.price}'


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
        widget=SelectWithOptionAttributes(),
    )
    request_date = forms.DateField(required=True, label="", widget=DateInput())
    passengers = forms.IntegerField(label="", widget=NumberInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = "destinations"
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
        destination = self.cleaned_data.get('destination')
        request_date = self.cleaned_data.get('request_date')
        passengers = self.cleaned_data.get('passengers')

        if not isinstance(destination, Destination):
            self._errors['destimation'] = self.error_class([
                'Please choose an option from the list'])

        elif passengers > destination.max_passengers:
            self._errors['passengers'] = self.error_class([
                'Sorry, this exceeds the maximum for selected trip'])

        elif passengers < 0:
            self._errors['passengers'] = self.error_class([
                'Please choose at least one passenger'])

        if request_date < date.today():
            self._errors['request_date'] = self.error_class([
                'Searched date should not be in the past'])

        # return any errors if found
        return self.cleaned_data


class DateChoiceForm(ModelForm):
    """
    Provides user a choice of available dates relative to their preference.
    Uses 'radio' type input which allows only one option to be selected.
    By default the closest date to the users searched date is selected.
    """

    class Meta:
        model = Booking
        fields = ["trip"]
        field_classes = {"trip": TripChoiceField}
        widgets = {"trip": RadioSelect()}

    def __init__(self, *args, **kwargs):
        trip_dates = kwargs.pop("trips", None)
        super(DateChoiceForm, self).__init__(*args, **kwargs)
        self.fields["trip"].queryset = trip_dates


class RequiredPassengerFormSet(BaseInlineFormSet):
    """ Validates that all forms in the formset are completed """

    def __init__(self, *args, **kwargs):
        super(RequiredPassengerFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class InputPassengersForm(ModelForm):
    """ Customises validation for Passenger form """

    class Meta:
        model = Booking
        fields = ('trip',)
        widgets = {'trip': HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(InputPassengersForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field("trip"),
                Div(
                    Fieldset(
                        'Add passengers',
                        Formset('passenger_formset'),
                        css_class="border col-12"
                    ), css_class="col-8"
                ),
                ButtonHolder(Submit(
                    'submit', 'Save', css_class="btn btn-outline"
                ), css_class="col-12"),
                css_class="row border justify-items-center"
            )
        )


class BookingPaymentForm(forms.ModelForm):
    """ Form to collect payment information to conclude the booking """

    class Meta:
        model = Booking
        fields = (
            "trip",
        )

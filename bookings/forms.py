from django import forms
from django.forms import ModelChoiceField
from django.forms.widgets import Select
from .models import Destination
from datetime import date


class DateInput(forms.DateInput):
    """ https://www.youtube.com/watch?v=I2-JYxnSiB0 """

    input_type = "date"


class SelectWithOptionAttribute(Select):
    """
    Select with Option Attributes- subclasses Django's select widget
    and created a dictionary of labels which become attributes
    Code suggested in this StackOverflow post:
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
    """ChoiceField which puts num_passengers on <options>"""

    widget = SelectWithOptionAttribute

    def label_from_instance(self, obj):
        # 'obj' will be a Destination
        return {
            # the usual label:
            'label': super().label_from_instance(obj),
            # the new data attribute:
            'data-max-num': obj.max_passengers
        }


class InitialForm(forms.Form):
    """
    Collects user's desired deestination, no. of passengers and date preference
    """

    destination = DestinationChoiceField(queryset=Destination.objects.all())
    request_date = forms.DateField(
        required=True,
        widget=DateInput(
            attrs={
                "min": date.today(),
                "max": "2040-12-20",
            }
        ),
    )
    passengers = forms.IntegerField()
    passengers.widget.attrs.update(
        {"min": 1, "disabled": True, "id": "passengers-max"}
    )
    destination.widget.attrs.update({"id": "selected-trip"})

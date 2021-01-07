"""
Creates Formset layout object and creates the formset.
"""
from django.core.exceptions import ValidationError
from django import forms
from django.template.loader import render_to_string
from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from .models import Booking, Passenger


class Formset(LayoutObject):
    """
    Credit:
    https://stackoverflow.com/questions/15157262/django-crispy-forms-nesting-a-formset-within-a-form/22053952#22053952
    Create a new fieldtype that renders a formset as though it were a field
    """

    template = 'bookings/forms/formset.html'

    def __init__(self, formset_name_in_context, template=None):
        self.formset_name_in_context = formset_name_in_context

        # Fields property required by crispy_forms/layout.py
        self.fields = []

        # Creates an instance level variable from the variable 'template'
        if template:
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context[self.formset_name_in_context]
        return render_to_string(self.template, {'formset': formset})


def make_passenger_formset(form, passenger_total):
    """Receives a dynamic value to be used in construction of inlineformset."""

    PassengerFormSet = forms.inlineformset_factory(
        Booking,
        Passenger,
        form=form,
        formset=RequiredPassengerFormSet,
        extra=passenger_total,
        max_num=passenger_total,
        min_num=passenger_total,
        validate_max=True,
        validate_min=True,
        can_delete=False,
    )

    return PassengerFormSet


class RequiredPassengerFormSet(forms.BaseInlineFormSet):
    """
    Validation for the formset as a whole.
    Validates that all forms in the formset are completed and no passenger is
    entered more than once.
    """

    def __init__(self, *args, **kwargs):
        super(RequiredPassengerFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

    def full_clean(self):
        super(RequiredPassengerFormSet, self).full_clean()

        for error in self._non_form_errors.as_data():
            if error.code == 'too_few_forms':
                error.message = "Please provide details for all %d \
                    travellers." % self.min_num

    def clean(self):
        if any(self.errors):
            return
        passengers = []
        for form in self.forms:
            passport_no = form.cleaned_data.get("passport_no")
            if passport_no in passengers:
                raise ValidationError("Duplicate passenger")
            passengers.append(passport_no)

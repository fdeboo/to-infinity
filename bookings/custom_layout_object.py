"""
Credit to https://stackoverflow.com/questions/15157262/django-crispy-forms-nesting-a-formset-within-a-form/22053952#22053952
"""

from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from django.template.loader import render_to_string


class Formset(LayoutObject):
    """
    Create a new fieldtype that renders a formset as though it were just a field
    """

    template = 'bookings/formset.html'

    def __init__(self, formset_name_in_context, template=None):
        self.formset_name_in_context = formset_name_in_context
        self.fields = []  # Fields property required by crispy_forms/layout.py
        if template:  # Creates an instance level variable from variable 'template'
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context[self.formset_name_in_context]
        return render_to_string(self.template, {'formset': formset})

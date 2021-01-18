""" Creates form based on UserProfile model """
from django import forms
from .models import UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Submit,
    Field,
    Div,
    ButtonHolder
)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            "first_name",
            "last_name",
            "default_phone_num",
            "default_passport_num",
        )

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "default_phone_num": "Phone Number",
            "default_passport_num": "Passport Number",
        }

        self.fields["default_phone_num"].widget.attrs["autofocus"] = True
        for field in self.fields:
            placeholder = placeholders[field]
            self.fields[field].widget.attrs["placeholder"] = placeholder
            self.fields[field].widget.attrs[
                "class"
            ] = "border-black rounded-0 \
                all-form-input"
            self.fields[field].label = False
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Div(
                Field(
                    "first_name",
                ),
                Field(
                    "last_name",
                ),
                Field(
                    "default_phone_num",
                ),
                Field(
                    "default_passport_num",
                ),
            ),
            ButtonHolder(
                Submit("submit", "Save", css_class="m-0 btn btn-outline"),
            ),
        )

from django import forms
from .models import Account


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["username", "email", "role"]


class UbahPasswordForm(forms.Form):
    current_password = forms.CharField(max_length=100)
    new_password = forms.CharField(max_length=100)
    confirmation_password = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirmation_password = cleaned_data.get("confirmation_password")

        if password != confirmation_password:
            raise forms.ValidationError("Passwords do not match")
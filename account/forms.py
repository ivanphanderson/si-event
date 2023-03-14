from django import forms
from .models import Account
from django.contrib.auth.forms import UserCreationForm

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'username',
            'email',
            'role'
        ]
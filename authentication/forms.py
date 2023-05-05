from django import forms

class ForgetPasswordForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()

class NewPasswordForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(max_length=100)
    confirmation_password = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmation_password = cleaned_data.get("confirmation_password")

        if password != confirmation_password:
            raise forms.ValidationError("Passwords do not match")

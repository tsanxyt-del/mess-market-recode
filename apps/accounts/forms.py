"""Login / profile / password forms."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Username or email", "autocomplete": "username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Password", "autocomplete": "current-password"})
    )


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-input"}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={"class": "form-input"}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": "form-input"}))


class AdminPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})

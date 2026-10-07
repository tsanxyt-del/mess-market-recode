"""Item forms."""
from django import forms
from apps.market.constants import UNITS
from .constants import CATEGORIES


class ItemForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(
        attrs={"class": "form-input", "placeholder": "e.g. Rice"}))
    default_unit = forms.ChoiceField(choices=UNITS, widget=forms.Select(attrs={"class": "form-input"}))
    category = forms.ChoiceField(
        choices=[(c, c) for c in CATEGORIES],
        widget=forms.Select(attrs={"class": "form-input"}))
    aliases = forms.CharField(required=False, max_length=400, widget=forms.TextInput(
        attrs={"class": "form-input", "placeholder": "Aloo, Tamatar (Hindi naam, comma se)"}))

"""Market forms (admin)."""
from django import forms
from .constants import UNITS


class PurchaseForm(forms.Form):
    purchase_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-input", "id": "id_purchase_date"}))
    item_id = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"id": "id_item_id"}))
    item_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-input", "id": "id_item_name",
                                      "placeholder": "Type or select item…", "autocomplete": "off", "list": "item-list"}))
    quantity = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-input", "id": "id_quantity", "step": "0.01", "min": "0.01"}))
    unit = forms.ChoiceField(choices=UNITS, widget=forms.Select(attrs={"class": "form-input", "id": "id_unit"}))
    rate = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-input", "id": "id_rate", "step": "0.01", "min": "0"}))
    bill_file = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "form-input", "id": "id_bill"}))
    remark = forms.CharField(required=False, max_length=500, widget=forms.Textarea(
        attrs={"class": "form-input", "rows": 2, "placeholder": "Remark (optional)", "maxlength": "500"}))

"""Bill upload form."""
from django import forms


class BillUploadForm(forms.Form):
    bill = forms.FileField(widget=forms.FileInput(attrs={"class": "form-input", "accept": ".jpg,.jpeg,.png,.webp,.pdf"}))
    purchase_date = forms.DateField(required=False, widget=forms.DateInput(
        attrs={"type": "date", "class": "form-input"}))

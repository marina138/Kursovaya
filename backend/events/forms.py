from django import forms
from .models import Product
import re


class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1, initial=1)


class PhoneForm(forms.Form):
    phone = forms.CharField(max_length=15)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        pattern = r'^\+7\d{10}$'
        if not re.match(pattern, phone):
            raise forms.ValidationError("Введите телефон в формате +7XXXXXXXXXX")
        return phone


class AddressForm(forms.Form):
    address = forms.CharField(max_length=255, min_length=10)

    def clean_address(self):
        address = self.cleaned_data['address']
        if len(address.strip()) < 10:
            raise forms.ValidationError("Пожалуйста, введите полный адрес доставки (не менее 10 символов).")
        return address

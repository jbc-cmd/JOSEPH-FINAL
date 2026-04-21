import re

from django import forms

from .models import DeliveryAddress


NAME_PATTERN = re.compile(r"^[A-Za-z]+(?:[ '.-][A-Za-z]+)*$")
LABEL_PATTERN = re.compile(r"^[A-Za-z0-9]+(?:[ '&().,-][A-Za-z0-9]+)*$")
PHONE_SANITIZE_PATTERN = re.compile(r"[\s\-()]")
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")


class DeliveryAddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing_class + ' field-input').strip()

        if self.is_bound:
            for field_name in self.errors:
                if field_name in self.fields:
                    widget = self.fields[field_name].widget
                    existing_class = widget.attrs.get('class', '')
                    widget.attrs['class'] = (existing_class + ' field-error').strip()
                    widget.attrs['aria-invalid'] = 'true'

    class Meta:
        model = DeliveryAddress
        fields = [
            'label',
            'recipient_name',
            'phone_number',
            'address',
            'city',
            'postal_code',
            'notes',
            'is_default',
        ]
        widgets = {
            'label': forms.TextInput(
                attrs={
                    'autocomplete': 'address-line1',
                    'maxlength': '100',
                    'placeholder': 'Home, Office, Mama House',
                }
            ),
            'recipient_name': forms.TextInput(
                attrs={
                    'autocomplete': 'name',
                    'maxlength': '255',
                    'placeholder': 'Juan Dela Cruz',
                }
            ),
            'phone_number': forms.TextInput(
                attrs={
                    'inputmode': 'tel',
                    'autocomplete': 'tel',
                    'maxlength': '20',
                    'placeholder': '09XXXXXXXXX',
                }
            ),
            'address': forms.TextInput(
                attrs={
                    'autocomplete': 'street-address',
                    'maxlength': '255',
                    'placeholder': 'Blk 1 Lot 2, Purok 3, Barangay San Juan',
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'autocomplete': 'address-level2',
                    'maxlength': '100',
                    'placeholder': 'Surigao City',
                }
            ),
            'postal_code': forms.TextInput(
                attrs={
                    'inputmode': 'numeric',
                    'pattern': r'[0-9]*',
                    'autocomplete': 'postal-code',
                    'maxlength': '20',
                    'placeholder': '8400',
                }
            ),
            'notes': forms.TextInput(
                attrs={
                    'maxlength': '300',
                    'placeholder': 'Leave at the gate or call upon arrival',
                }
            ),
        }

    def clean_label(self):
        label = (self.cleaned_data.get('label') or '').strip()
        if len(label) < 2:
            raise forms.ValidationError('Label must be at least 2 characters.')
        if not LABEL_PATTERN.fullmatch(label):
            raise forms.ValidationError('Label contains unsupported characters.')
        return label

    def clean_recipient_name(self):
        recipient_name = re.sub(r"\s+", " ", (self.cleaned_data.get('recipient_name') or '').strip())
        if len(recipient_name) < 2:
            raise forms.ValidationError('Recipient name must be at least 2 characters.')
        if not NAME_PATTERN.fullmatch(recipient_name):
            raise forms.ValidationError('Recipient name can only use letters, spaces, apostrophes, periods, and hyphens.')
        return recipient_name

    def clean_phone_number(self):
        raw_phone_number = (self.cleaned_data.get('phone_number') or '').strip()
        phone_number = PHONE_SANITIZE_PATTERN.sub('', raw_phone_number)
        if not PHONE_PATTERN.fullmatch(phone_number):
            raise forms.ValidationError('Enter a valid phone number using 10 to 15 digits.')
        return phone_number

    def clean_address(self):
        address = re.sub(r"\s+", " ", (self.cleaned_data.get('address') or '').strip())
        if len(address) < 10:
            raise forms.ValidationError('Address must be at least 10 characters.')
        if len(address) > 255:
            raise forms.ValidationError('Address must be 255 characters or fewer.')
        return address

    def clean_city(self):
        city = re.sub(r"\s+", " ", (self.cleaned_data.get('city') or '').strip())
        if len(city) < 2:
            raise forms.ValidationError('City must be at least 2 characters.')
        if not NAME_PATTERN.fullmatch(city):
            raise forms.ValidationError('City can only use letters, spaces, apostrophes, periods, and hyphens.')
        return city

    def clean_postal_code(self):
        postal_code = (self.cleaned_data.get('postal_code') or '').strip()
        if postal_code and not postal_code.isdigit():
            raise forms.ValidationError('Postal code must contain numbers only.')
        return postal_code

    def clean_notes(self):
        notes = re.sub(r"\s+", " ", (self.cleaned_data.get('notes') or '').strip())
        if len(notes) > 300:
            raise forms.ValidationError('Delivery notes must be 300 characters or fewer.')
        return notes

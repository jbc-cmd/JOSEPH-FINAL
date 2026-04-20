from django import forms

from .models import DeliveryAddress


class DeliveryAddressForm(forms.ModelForm):
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
            'postal_code': forms.TextInput(
                attrs={
                    'inputmode': 'numeric',
                    'pattern': r'[0-9]*',
                    'autocomplete': 'postal-code',
                    'maxlength': '20',
                }
            ),
        }

    def clean_postal_code(self):
        postal_code = (self.cleaned_data.get('postal_code') or '').strip()
        if postal_code and not postal_code.isdigit():
            raise forms.ValidationError('Postal code must contain numbers only.')
        return postal_code

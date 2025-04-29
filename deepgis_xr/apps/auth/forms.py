from django import forms
from phonenumber_field.formfields import PhoneNumberField

class PhoneLoginForm(forms.Form):
    phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={'placeholder': '+1234567890'})
    )

class VerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit code',
            'type': 'number'
        })
    ) 
from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """Form for creating orders"""
    
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'country',
            'payment_method', 'customer_notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+254 700 000 000'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Postal Code (Optional)'}),
            'country': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Country'}),
            'customer_notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Order notes (optional)'}),
        }

from django import forms
from .models import Branch
import re # Para limpieza de teléfono

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = [
            'name', 'phone', 'address',
            'district', 'email', 'active' 
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            return name.strip()
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            return phone.strip()
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.lower().strip()
        return email

    def clean_district(self):
        return self.cleaned_data.get('district')
from django import forms
from .models import Customer
from django.core.exceptions import ValidationError

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'document_type', 'document_number',
            'address', 'phone', 'email', 'customer_type', 'birth_date',
            'status', 'reference', 'notes'
        ]
        error_messages = {
            'document_type': {
                'required': "Debe seleccionar un tipo de documento.",
                'invalid_choice': "El tipo de documento seleccionado no es válido."
            },
            'document_number': {
                'required': "El número de documento es obligatorio."
            },
            'email': {
                'unique': "Este correo electrónico ya está registrado."
            }
        }

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name')
        if name:
            return name.strip()
        return name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            return last_name.strip()
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.strip().lower()
        return email

    def clean(self):
        cleaned_data = super().clean()
        
        document_type = cleaned_data.get("document_type")
        document_number = cleaned_data.get("document_number")

        if document_type and document_number:
            query = Customer.objects.filter(document_type=document_type, document_number=document_number)
            
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                self.add_error('document_number', ValidationError(
                    "Ya existe un cliente con este tipo y número de documento.",
                    code='unique_together'
                ))

        try:
            instance = self.instance or Customer(**self.cleaned_data)
            for field, value in self.cleaned_data.items():
                setattr(instance, field, value)
            
            instance.clean()
        except ValidationError as e:
            self.add_error(None, e)

        return cleaned_data
from django import forms
from .models import VehicleCategory

class VehicleCategoryForm(forms.ModelForm):

    class Meta:
        model = VehicleCategory
        fields = ['name']
        error_messages = {
            'name': {
                'required': "El nombre de la categoría es obligatorio.",
                'unique': "Esta categoría ya se encuentra registrada. Por favor, ingrese un nombre diferente."
            }
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            return name.strip()
        return name
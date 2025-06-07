from django import forms
from .models import Brand

class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        fields = ['name']
        error_messages = {
            'name': {
                'required': "El nombre de la marca es obligatorio.",
                'unique': "Esta marca ya se encuentra registrada. Por favor, ingrese un nombre diferente."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            return name.strip()
        return name
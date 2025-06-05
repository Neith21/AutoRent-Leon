from django import forms
from .models import VehicleModel
from brand.models import Brand

class VehicleModelForm(forms.ModelForm):
    class Meta:
        model = VehicleModel
        fields = [
            'name', 
            'brand',
        ]
        error_messages = {
            'brand': {
                'invalid_choice': "La marca seleccionada no existe o no es válida.",
                'required': "Debe seleccionar una marca para el modelo.",
                'null': "La marca no puede estar vacía para el modelo.",
            },
            'name': {
                'required': "El nombre del modelo es obligatorio.",
                'blank': "El nombre del modelo no puede estar vacío.",
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].queryset = Brand.objects.filter(active=True)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            return name.strip()
        return name

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        brand = cleaned_data.get("brand")

        if name and brand:
            # Si es una actualización (self.instance.pk existe)
            # y el nombre y marca no han cambiado, o si han cambiado pero no colisionan.
            query = VehicleModel.objects.filter(name=name, brand=brand)
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                self.add_error('name', forms.ValidationError(
                    "Ya existe un modelo con este nombre para la marca seleccionada.",
                    code='unique_together'
                ))
        return cleaned_data
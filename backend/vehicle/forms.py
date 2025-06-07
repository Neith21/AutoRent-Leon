from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'plate', 'vehiclemodel', 'vehiclecategory', 'branch', 'color', 'year',
            'engine', 'engine_type', 'engine_number', 'vin',
            'seat_count', 'daily_price', 'description', 'status'
        ]
        error_messages = {
            'vehiclemodel': {
                'invalid_choice': "El modelo de vehículo seleccionado no existe o no es válido.",
            },
            'vehiclecategory': {
                'invalid_choice': "La categoría de vehículo seleccionada no existe o no es válida.",
            },
            'branch': {
                'invalid_choice': "La sucursal seleccionada no existe o no es válida.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def clean_plate(self):
        plate = self.cleaned_data.get('plate')
        if plate: return plate.upper().strip()
        return plate

    def clean_vin(self):
        vin = self.cleaned_data.get('vin')
        if vin: return vin.upper().strip()
        return vin
    
    def clean_color(self):
        color = self.cleaned_data.get('color')
        if color: return color.strip()
        return color

    def clean_engine_number(self):
        engine_number = self.cleaned_data.get('engine_number')
        if engine_number: return engine_number.strip()
        return engine_number
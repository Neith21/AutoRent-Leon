from django.db import models
from django.core.validators import RegexValidator
from brand.models import Brand
from simple_history.models import HistoricalRecords

# Create your models here.

class VehicleModel(models.Model):
    brand = models.ForeignKey(
        Brand,
        on_delete=models.RESTRICT,
        verbose_name="marca",
        help_text="Seleccione la marca del modelo del vehículo.",
        error_messages={
            'required': "Debe seleccionar una marca.",
            'invalid_choice': "La marca seleccionada no es válida.",
            'null': "La marca no puede estar vacía.",
            'blank': "La marca no puede estar en blanco.",
        }
    )
    name = models.CharField(
        max_length=100,
        verbose_name="nombre del modelo",
        help_text="Nombre del modelo del vehículo (ej. Corolla, Hilux, Civic). Máx. 100 caracteres.",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚüÜ\s\-\.]+$', # Permite letras, números, espacios, guiones y puntos
                message="El nombre del modelo solo puede contener letras, números, espacios, guiones (-) y puntos (.)."
            )
        ],
        error_messages={
            'required': "El nombre del modelo es obligatorio.",
            'blank': "El nombre del modelo no puede estar vacío.",
            'unique': "Ya existe un modelo con este nombre para esta marca.",
            'max_length': "El nombre del modelo no puede tener más de 100 caracteres."
        }
        # No se pone null=False porque CharField por defecto es null=False
        # No se pone blank=False porque CharField por defecto es blank=False
    )
    
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = 'vehiclemodel'
        verbose_name = 'Modelo de Vehículo'
        verbose_name_plural = 'Modelos de Vehículos'
        unique_together = [['brand', 'name']]

    def __str__(self):
        brand_name = self.brand.name if self.brand else "Marca Desconocida"
        return f"{brand_name} {self.name}"
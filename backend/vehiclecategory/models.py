from django.db import models
from django.core.validators import RegexValidator
from simple_history.models import HistoricalRecords

class VehicleCategory(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="nombre de la categoría",
        help_text="Nombre único de la categoría del vehículo (máx. 50 caracteres).",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-]+$',
                message="El nombre de la categoría solo puede contener letras, números, espacios y guiones."
            )
        ],
        error_messages={
            'required': "El nombre de la categoría es obligatorio.",
            'unique': "Esta categoría ya se encuentra registrada."
        }
    )

    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = 'vehiclecategory'
        verbose_name = 'Categoría de Vehículo'
        verbose_name_plural = 'Categorías de Vehículos'

    def __str__(self):
        return self.name
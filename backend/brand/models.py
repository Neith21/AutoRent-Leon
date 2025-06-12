from django.db import models
from django.core.validators import RegexValidator
from simple_history.models import HistoricalRecords

class Brand(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nombre de la marca",
        help_text="Nombre único de la marca del vehículo (máx. 100 caracteres).",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-&.]+$',
                message="El nombre de la marca solo puede contener letras, números, espacios, guiones, '&' o '.'."
            )
        ],
        error_messages={
            'required': "El nombre de la marca es obligatorio.",
            'unique': "Esta marca ya se encuentra registrada."
        }
    )

    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    history = HistoricalRecords(inherit=True)

    class Meta:
        db_table = 'brand'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.name

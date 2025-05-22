from django.db import models
from django.core.validators import RegexValidator
from municipality.models import Municipality

# Create your models here.

class District(models.Model):
    code = models.IntegerField(
        unique=True, # El código de distrito es único
        verbose_name="código de distrito",
        help_text="Código numérico único para el distrito.",
        error_messages={
            'unique': "Ya existe un distrito con este código."
        }
    )
    district = models.CharField(
        max_length=255,
        verbose_name="nombre del distrito",
        help_text="Nombre oficial del distrito. Solo se permiten letras, números, espacios y los caracteres: - . , # & ( ) '",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\.,#&()\'ñÑáéíóúÁÉÍÓÚ]+$',
                message="El nombre del distrito solo puede contener letras, números, espacios y los siguientes caracteres especiales: - . , # & ( ) '"
            )
        ],
        error_messages={
            'required': "El nombre del distrito es obligatorio.",
            'blank': "El nombre del distrito no puede estar vacío.",
        }
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        verbose_name="municipio al que pertenece",
        help_text="Municipio al que está asociado este distrito.",
        related_name="districts",
        error_messages={
            'required': "Debe seleccionar un municipio.",
            'invalid_choice': "El municipio seleccionado no es válido."
        }
    )

    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"{self.district} (Mun: {self.municipality.municipality})"

    class Meta:
        db_table = 'disctrict'
        verbose_name = 'Distrito'
        verbose_name_plural = 'Distritos'
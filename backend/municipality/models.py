from django.db import models
from django.core.validators import RegexValidator
from department.models import Department

# Create your models here.

class Municipality(models.Model):
    code = models.CharField(
        max_length=8,         # Máximo 8 números
        unique=True,
        verbose_name="código de municipio",
        help_text="Código numérico único de hasta 8 dígitos para el municipio.",
        validators=[
            RegexValidator(
                regex=r'^[0-9]+$', # Solo números
                message="El código de municipio solo puede contener números."
            )
        ],
        error_messages={
            'unique': "Ya existe un municipio con este código."
        }
    )
    municipality = models.CharField(
        max_length=255,
        verbose_name="nombre del municipio",
        help_text="Nombre oficial del municipio. Solo se permiten letras, números, espacios y los caracteres: - . , # & ( ) '",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\.,#&()\'ñÑáéíóúÁÉÍÓÚ]+$',
                message="El nombre del municipio solo puede contener letras, números, espacios y los siguientes caracteres especiales: - . , # & ( ) '"
            )
        ],
        error_messages={
            'required': "El nombre del municipio es obligatorio.",
            'blank': "El nombre del municipio no puede estar vacío.",
        }
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name="departamento al que pertenece",
        help_text="Departamento al que está asociado este municipio.",
        related_name="municipalities",
        error_messages={
            'required': "Debe seleccionar un departamento.",
            'invalid_choice': "El departamento seleccionado no es válido."
        }
    )
    
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="ID del creador")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="ID del modificador")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"{self.municipality} (Dep: {self.department.department if self.department else 'N/A'})"

    class Meta:
        db_table = 'municipality'
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['department', 'municipality']
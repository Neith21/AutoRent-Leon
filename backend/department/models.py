from django.db import models
from django.core.validators import RegexValidator

# Create your models here.


class Department(models.Model):
    code = models.IntegerField(
        unique=True, # El código de departamento es único
        verbose_name="código de departamento",
        help_text="Código numérico único para el departamento.",
        error_messages={
            'unique': "Ya existe un departamento con este código."
        }
    )
    department = models.CharField(
        max_length=255,
        verbose_name="nombre del departamento",
        help_text="Nombre oficial del departamento. Solo se permiten letras, números, espacios y los caracteres: - . , # & ( ) '",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\.,#&()\'ñÑáéíóúÁÉÍÓÚ]+$',
                message="El nombre del departamento solo puede contener letras, números, espacios y los siguientes caracteres especiales: - . , # & ( ) '"
            )
        ],
        error_messages={
            'required': "El nombre del departamento es obligatorio.",
            'blank': "El nombre del departamento no puede estar vacío.",
        }
    )
    
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return f"{self.department} (Cód: {self.code})"

    class Meta:
        db_table = 'department'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
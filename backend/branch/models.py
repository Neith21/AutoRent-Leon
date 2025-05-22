from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from district.models import District

class Branch(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nombre de la sucursal",
        help_text="Nombre completo de la sucursal (máx. 100 caracteres).",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\.,#&()\'ñÑáéíóúÁÉÍÓÚ]+$',
                message="El nombre solo puede contener letras, números, espacios y los siguientes caracteres: - . , # & ( ) '"
            )
        ],
        error_messages={
            'required': "El nombre de la sucursal es obligatorio.",
            'blank': "El nombre de la sucursal no puede estar vacío.",
            'unique': "Ya existe una sucursal con este nombre."
        }
    )
    phone = models.CharField(
        max_length=25,
        verbose_name="teléfono de contacto",
        help_text="Número de teléfono principal de la sucursal (ej. +503 2222-1111).",
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9\s\-\(\)]{7,24}$',
                message="Ingrese un número de teléfono válido (ej. +503 2222-1111). Puede incluir el código de país."
            )
        ],
        error_messages={
            'required': "El número de teléfono es obligatorio.",
            'blank': "El número de teléfono no puede estar vacío."
        }
    )
    address = models.TextField(
        verbose_name="dirección completa",
        help_text="Dirección física detallada de la sucursal.",
        error_messages={
            'required': "La dirección es obligatoria.",
            'blank': "La dirección no puede estar vacía."
        }
    )
    district = models.ForeignKey(
        District,
        on_delete=models.RESTRICT,
        verbose_name="distrito",
        help_text="Seleccione el distrito donde se ubica la sucursal.",
        related_name="branches",
        error_messages={
            'required': "El distrito es obligatorio.",
            'blank': "Debe seleccionar un distrito.",
            'invalid_choice': "El distrito seleccionado no es válido."
        }
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name="correo electrónico",
        help_text="Correo electrónico de contacto de la sucursal (debe ser único).",
        validators=[EmailValidator(message="Ingrese una dirección de correo electrónico válida.")],
        error_messages={
            'required': "El correo electrónico es obligatorio.",
            'blank': "El correo electrónico no puede estar vacío.",
            'unique': "Esta dirección de correo electrónico ya está registrada."
        }
    )

    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'branch'
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
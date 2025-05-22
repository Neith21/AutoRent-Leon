from django.db import models
from django.core.validators import (
    MinValueValidator, MaxValueValidator, RegexValidator
)
from django.utils import timezone
from vehiclemodel.models import VehicleModel
from vehiclecategory.models import VehicleCategory

def get_next_year():
    return timezone.now().year + 1

class Vehicle(models.Model):
    plate = models.CharField(
        max_length=8,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]{6,8}$',
                message="La placa debe tener entre 6 y 8 caracteres alfanuméricos en mayúsculas (ej. ABC123D o ABC1234)."
            )
        ],
        help_text="Placa única, sin espacios ni caracteres especiales, 6–8 caracteres (ej. ABC1234).",
        error_messages={
            'unique': "Esta placa ya está registrada.",
            'blank': "La placa no puede estar vacía.",
            'required': "La placa es un campo obligatorio." 
        }
    )
    vehiclemodel = models.ForeignKey(
        VehicleModel,
        on_delete=models.RESTRICT,
        verbose_name="modelo del vehículo",
        help_text="Seleccione el modelo del vehículo.",
        error_messages={
            'required': "Debe seleccionar un modelo de vehículo.",
            'invalid_choice': "El modelo de vehículo seleccionado no es válido."
        }
    )
    vehiclecategory = models.ForeignKey(
        VehicleCategory,
        on_delete=models.RESTRICT,
        verbose_name="categoría del vehículo",
        help_text="Seleccione la categoría del vehículo.",
        error_messages={
            'required': "Debe seleccionar una categoría de vehículo.",
            'invalid_choice': "La categoría de vehículo seleccionada no es válida."
        }
    )
    color = models.CharField(
        max_length=50,
        verbose_name="color",
        help_text="Color del vehículo (máx. 50 caracteres).",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s]+$',
                message="El color solo debe contener letras y espacios."
            )
        ],
        error_messages={
            'required': "El color del vehículo es obligatorio.",
            'max_length': "El color no puede tener más de 50 caracteres."
        }
    )
    year = models.PositiveIntegerField(
        verbose_name="año de fabricación",
        validators=[
            MinValueValidator(1886, message="El año de fabricación no puede ser anterior a 1886."),
            MaxValueValidator(
                get_next_year,
                message="El año de fabricación no puede ser mayor al siguiente año del actual."
            )
        ],
        help_text="Año de fabricación del vehículo (ej. 2023).",
        error_messages={
            'required': "El año de fabricación es obligatorio.",
            'invalid': "Ingrese un año válido."
        }
    )
    engine = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="descripción del motor",
        help_text="Modelo o cilindrada del motor (ej. ‘2GR-FE’ o ‘1998 cc’). Máx. 30 caracteres. Opcional.",
        error_messages={
            'max_length': "La descripción del motor no puede tener más de 30 caracteres."
        }
    )

    ENGINE_TYPE_CHOICES = [
        ("Gasolina", "Gasolina"),
        ("Diesel", "Diesel"),
        ("Electrico", "Eléctrico"),
        ("Hibrido", "Híbrido"),
        ("GLP", "GLP"),
    ]
    engine_type = models.CharField(
        max_length=10,
        choices=ENGINE_TYPE_CHOICES,
        verbose_name="tipo de motor",
        help_text="Seleccione el tipo de motor.",
        error_messages={
            'required': "Debe seleccionar un tipo de motor.",
            'invalid_choice': "El tipo de motor seleccionado no es una opción válida."
        }
    )
    engine_number = models.CharField(
        max_length=17,
        unique=True,
        verbose_name="número de motor",
        help_text="Número de serie del motor (único, máx. 17 caracteres). Puede ser alfanumérico.",
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]+$',
                message="El número de motor solo debe contener letras mayúsculas y números."
            )
        ],
        error_messages={
            'unique': "Este número de motor ya está registrado.",
            'required': "El número de motor es obligatorio.",
            'max_length': "El número de motor no puede tener más de 17 caracteres."
        }
    )
    vin = models.CharField(
        max_length=17,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-HJ-NPR-Z0-9]{17}$', # VIN estándar no usa I, O, Q
                message="VIN inválido: debe tener 17 caracteres alfanuméricos y no debe contener las letras I, O, Q."
            )
        ],
        verbose_name="VIN (Número de Identificación Vehicular)",
        help_text="VIN único de 17 caracteres (sin I, O, Q).",
        error_messages={
            'unique': "Este VIN ya está registrado.",
            'required': "El VIN es obligatorio.",
            'max_length': "El VIN debe tener exactamente 17 caracteres."
        }
    )
    seat_count = models.PositiveIntegerField(
        verbose_name="cantidad de asientos",
        validators=[
            MinValueValidator(1, message="La cantidad de asientos debe ser como mínimo 1."),
            MaxValueValidator(50, message="La cantidad de asientos no puede exceder los 50.")
        ],
        help_text="Número de asientos (incluyendo conductor), entre 1 y 50.",
        error_messages={
            'required': "La cantidad de asientos es obligatoria.",
            'invalid': "Ingrese una cantidad de asientos válida."
        }
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripción adicional",
        help_text="Cualquier detalle o descripción adicional sobre el vehículo. Opcional.",
    )

    STATUS_CHOICES = [
        ('Disponible', 'Disponible'),
        ('En mantenimiento', 'En mantenimiento'),
        ('En reparacion', 'En reparación'),
        ('Reservado', 'Reservado'),
        ('Alquilado', 'Alquilado'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Disponible',
        verbose_name="estado del vehículo",
        help_text="Seleccione el estado actual del vehículo.",
        error_messages={
            'required': "Debe seleccionar un estado para el vehículo.",
            'invalid_choice': "El estado seleccionado no es una opción válida."
        }
    )

    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    class Meta:
        db_table = 'vehicle'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f"{self.plate} ({self.vehiclemodel})"
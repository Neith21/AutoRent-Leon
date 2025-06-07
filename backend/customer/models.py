from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from datetime import date

def get_min_birth_date():
    """
    Calcula la fecha de nacimiento máxima para que una persona sea mayor de edad (18 años).
    """
    return (timezone.now() - timezone.timedelta(days=18*365.25)).date()

def validate_birth_date(value):
    """
    Valida que la fecha de nacimiento corresponda a alguien mayor de 18 años.
    """
    min_birth_date = get_min_birth_date()
    if value > min_birth_date:
        raise ValidationError(f"El cliente debe ser mayor de 18 años (nacido antes del {min_birth_date.strftime('%d-%m-%Y')}).")

class Customer(models.Model):
    # --- Choices para los campos ENUM ---
    DOCUMENT_TYPE_CHOICES = [
        ('DUI', 'DUI'),
        ('Pasaporte', 'Pasaporte'),
    ]

    CUSTOMER_TYPE_CHOICES = [
        ('Nacional', 'Nacional'),
        ('Extranjero', 'Extranjero'),
    ]

    STATUS_CHOICES = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
        ('Lista Negra', 'Lista Negra'),
    ]

    # --- Campos del Modelo ---
    first_name = models.CharField(
        max_length=100,
        verbose_name="nombres",
        help_text="Nombres del cliente (máx. 100 caracteres).",
        error_messages={
            'required': "El nombre es un campo obligatorio.",
            'max_length': "El nombre no puede exceder los 100 caracteres."
        }
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="apellidos",
        help_text="Apellidos del cliente (máx. 100 caracteres).",
        error_messages={
            'required': "El apellido es un campo obligatorio.",
            'max_length': "El apellido no puede exceder los 100 caracteres."
        }
    )
    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name="tipo de documento",
        help_text="Seleccione el tipo de documento de identificación.",
        error_messages={
            'required': "Debe seleccionar un tipo de documento.",
            'invalid_choice': "El tipo de documento seleccionado no es válido."
        }
    )
    document_number = models.CharField(
        max_length=50,
        verbose_name="número de documento",
        help_text="Número del documento de identificación (DUI o Pasaporte).",
        error_messages={
            'required': "El número de documento es obligatorio.",
            'unique': "Este número de documento ya está registrado con este tipo de documento."
        }
    )
    address = models.TextField(
        verbose_name="dirección",
        help_text="Dirección de residencia del cliente.",
        error_messages={
            'required': "La dirección es obligatoria."
        }
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="teléfono",
        help_text="Número de teléfono de contacto. Formato para El Salvador: 1234-5678.",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$',
                message="El número de teléfono debe tener un formato válido (ej. 7777-7777 o +50377777777)."
            )
        ],
        error_messages={
            'required': "El número de teléfono es obligatorio."
        }
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name="correo electrónico",
        help_text="Correo electrónico único del cliente.",
        error_messages={
            'required': "El correo electrónico es obligatorio.",
            'unique': "Este correo electrónico ya está registrado."
        }
    )
    customer_type = models.CharField(
        max_length=10,
        choices=CUSTOMER_TYPE_CHOICES,
        verbose_name="tipo de cliente",
        help_text="Indique si el cliente es nacional o extranjero.",
        error_messages={
            'required': "Debe seleccionar el tipo de cliente."
        }
    )
    birth_date = models.DateField(
        verbose_name="fecha de nacimiento",
        help_text="El cliente debe ser mayor de 18 años.",
        validators=[
            MinValueValidator(
                limit_value=date(1900, 1, 1),
                message="La fecha de nacimiento no puede ser anterior a 1900."
            ),
            validate_birth_date
        ],
        error_messages={
            'required': "La fecha de nacimiento es obligatoria.",
            'invalid': "Ingrese una fecha válida."
        }
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Activo',
        verbose_name="estado del cliente",
        help_text="Estado actual del cliente en el sistema.",
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="referencia",
        help_text="Contacto de referencia del cliente (opcional)."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="notas adicionales",
        help_text="Cualquier nota relevante sobre el cliente (opcional)."
    )
    
    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def clean(self):
        """
        Validaciones personalizadas para el modelo.
        """
        super().clean()
        # Validar formato de DUI
        if self.document_type == 'DUI':
            dui_regex = r'^\d{8}-\d{1}$'
            if not RegexValidator(regex=dui_regex)(self.document_number):
                raise ValidationError({
                    'document_number': 'El formato del DUI debe ser 00000000-0.'
                })
        # Validar formato de Pasaporte (ejemplo general)
        elif self.document_type == 'Pasaporte':
            passport_regex = r'^[A-Z0-9]{6,15}$'
            if not RegexValidator(regex=passport_regex, message="El pasaporte debe contener entre 6 y 15 caracteres alfanuméricos.")(self.document_number):
                 raise ValidationError({
                    'document_number': 'El pasaporte debe contener entre 6 y 15 caracteres alfanuméricos.'
                })

    class Meta:
        db_table = 'customer'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        # Restricción UNIQUE para la combinación de tipo y número de documento
        unique_together = ('document_type', 'document_number')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
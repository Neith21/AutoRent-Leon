from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Company(models.Model):
    # --- Choices para la clasificación de la empresa ---
    CLASSIFICATION_CHOICES = [
        ('Pequeña', 'Pequeña'),
        ('Mediana', 'Mediana'),
        ('Gran', 'Gran Contribuyente'),
    ]

    trade_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nombre comercial",
        help_text="Nombre comercial de la empresa.",
        error_messages={'unique': "Ya existe una empresa con este nombre comercial."}
    )
    nrc = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="NRC (Número de Registro de Contribuyente)",
        help_text="Número de Registro de Contribuyente (ej. 12345-6).",
        validators=[
            RegexValidator(
                regex=r'^\d{1,6}-\d{1}$',
                message="El formato del NRC debe ser, por ejemplo, 12345-6."
            )
        ],
        error_messages={'unique': "Este NRC ya está registrado."}
    )
    classification = models.CharField(
        max_length=20,
        choices=CLASSIFICATION_CHOICES,
        verbose_name="clasificación",
        help_text="Clasificación de la empresa según su tamaño o tipo de contribuyente."
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="teléfono de la empresa",
        help_text="Número de teléfono de contacto de la empresa.",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$',
                message="El número de teléfono debe tener un formato válido."
            )
        ]
    )
    address = models.TextField(
        verbose_name="dirección fiscal",
        help_text="Dirección fiscal o principal de la empresa."
    )
    logo = models.URLField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="URL del Logotipo"
    )
    logo_public_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cloudinary Public ID del Logo"
    )
    logo_lqip = models.URLField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Logo de Baja Calidad (LQIP)"
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name="correo electrónico de la empresa",
        help_text="Correo electrónico principal de la empresa.",
        error_messages={'unique': "Este correo electrónico ya está registrado."}
    )
    website = models.URLField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="sitio web",
        help_text="Página web de la empresa (opcional)."
    )

    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def clean(self):
        """
        Asegura que solo exista una instancia de la empresa en la base de datos.
        """
        if Company.objects.exists() and not self.pk:
            raise ValidationError("Solo puede existir una instancia de la empresa en el sistema.")
        super().clean()

    class Meta:
        db_table = 'company'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresa'

    def __str__(self):
        return self.trade_name
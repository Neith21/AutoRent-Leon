from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

from customer.models import Customer
from vehicle.models import Vehicle
from branch.models import Branch

class Rental(models.Model):
    # --- Choices para los campos ENUM ---
    STATUS_CHOICES = [
        ('Reservado', 'Reservado'),
        ('Activo', 'Activo'),
        ('Finalizado', 'Finalizado'),
        ('Retrasado', 'Retrasado'),
        ('Cancelado', 'Cancelado'),
    ]

    FUEL_LEVEL_CHOICES = [
        ('Vacio', 'Vacío'),
        ('1/4', '1/4'),
        ('1/2', '1/2'),
        ('3/4', '3/4'),
        ('Lleno', 'Lleno'),
    ]

    # --- Relaciones (Foreign Keys) ---
    customer = models.ForeignKey(
        Customer,
        on_delete=models.RESTRICT,
        verbose_name="cliente",
        help_text="Cliente que realiza el alquiler.",
        error_messages={'required': "Debe seleccionar un cliente."}
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.RESTRICT,
        verbose_name="vehículo",
        help_text="Vehículo a alquilar.",
        error_messages={'required': "Debe seleccionar un vehículo."}
    )
    pickup_branch = models.ForeignKey(
        Branch,
        on_delete=models.RESTRICT,
        related_name='pickup_rentals', # related_name para evitar conflictos
        verbose_name="sucursal de recogida",
        help_text="Sucursal donde el cliente recogerá el vehículo.",
        error_messages={'required': "Debe seleccionar una sucursal de recogida."}
    )
    return_branch = models.ForeignKey(
        Branch,
        on_delete=models.RESTRICT,
        related_name='return_rentals', # related_name para evitar conflictos
        verbose_name="sucursal de devolución",
        help_text="Sucursal donde el cliente devolverá el vehículo.",
        error_messages={'required': "Debe seleccionar una sucursal de devolución."}
    )

    # --- Fechas del Alquiler ---
    start_date = models.DateTimeField(
        verbose_name="fecha y hora de inicio",
        help_text="Momento exacto en que inicia el alquiler.",
        error_messages={'required': "La fecha de inicio es obligatoria."}
    )
    end_date = models.DateTimeField(
        verbose_name="fecha y hora de fin",
        help_text="Momento exacto en que debe finalizar el alquiler.",
        error_messages={'required': "La fecha de fin es obligatoria."}
    )
    actual_return_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="fecha y hora de devolución real",
        help_text="Momento exacto en que el vehículo fue devuelto (se llena al finalizar)."
    )

    # --- Detalles y Estado del Alquiler ---
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Reservado',
        verbose_name="estado del alquiler",
        help_text="Estado actual del proceso de alquiler."
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="precio total calculado",
        help_text="Costo total del alquiler por los días solicitados.",
        validators=[MinValueValidator(0.01)],
        error_messages={
            'required': "El precio total es obligatorio.",
            'invalid': "Ingrese un precio válido."
        }
    )
    fuel_level_pickup = models.CharField(
        max_length=10,
        choices=FUEL_LEVEL_CHOICES,
        verbose_name="nivel de combustible (recogida)",
        help_text="Nivel de combustible al momento de entregar el vehículo.",
        error_messages={'required': "Debe especificar el nivel de combustible en la recogida."}
    )
    fuel_level_return = models.CharField(
        max_length=10,
        choices=FUEL_LEVEL_CHOICES,
        null=True,
        blank=True,
        verbose_name="nivel de combustible (devolución)",
        help_text="Nivel de combustible al momento de recibir el vehículo."
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name="observaciones",
        help_text="Notas o comentarios adicionales sobre el alquiler (daños, acuerdos, etc.)."
    )

    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    def clean(self):
        """
        Validaciones personalizadas para el modelo de alquiler.
        """
        super().clean()
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError({
                    'end_date': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
        
        if self.actual_return_date and self.start_date:
            if self.actual_return_date < self.start_date:
                raise ValidationError({
                    'actual_return_date': 'La fecha de devolución real no puede ser anterior a la fecha de inicio del alquiler.'
                })

    class Meta:
        db_table = 'rental'
        verbose_name = 'Alquiler'
        verbose_name_plural = 'Alquileres'

    def __str__(self):
        return f"Alquiler de {self.vehicle.plate} por {self.customer} - {self.start_date.strftime('%d/%m/%Y')}"

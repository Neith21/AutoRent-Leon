from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from rental.models import Rental

class Payment(models.Model):
    # --- Choices para los campos ENUM ---
    PAYMENT_TYPE_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta de Credito', 'Tarjeta de Crédito'),
        ('Tarjeta de Debito', 'Tarjeta de Débito'),
        ('Transferencia', 'Transferencia Bancaria'),
    ]

    CONCEPT_CHOICES = [
        ('Anticipo', 'Anticipo'),
        ('Pago Final', 'Pago Final'),
        ('Cargo Adicional', 'Cargo Adicional'), # Por ejemplo, por combustible o daños.
        ('Cargo por Retraso', 'Cargo por Retraso'), # Específico para días extra.
        ('Reembolso', 'Reembolso'), # Para devoluciones de depósitos o ajustes.
    ]
    
    # --- Relaciones y Campos Principales ---
    rental = models.ForeignKey(
        Rental,
        on_delete=models.CASCADE, # Si se elimina el alquiler, se eliminan sus pagos.
        verbose_name="alquiler asociado",
        help_text="El alquiler al que corresponde este pago.",
        error_messages={'required': "El pago debe estar asociado a un alquiler."}
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="monto del pago",
        help_text="La cantidad de dinero pagada o reembolsada.",
        validators=[MinValueValidator(0.01)],
        error_messages={
            'required': "El monto es un campo obligatorio.",
            'invalid': "Ingrese un monto válido."
        }
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        verbose_name="método de pago",
        help_text="El método utilizado para realizar el pago.",
        error_messages={'required': "Debe seleccionar un método de pago."}
    )
    payment_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="fecha y hora del pago",
        help_text="Momento exacto en que se realizó la transacción."
    )
    concept = models.CharField(
        max_length=20,
        choices=CONCEPT_CHOICES,
        verbose_name="concepto del pago",
        help_text="La razón o motivo del pago (anticipo, pago final, etc.).",
        error_messages={'required': "Debe especificar el concepto del pago."}
    )
    
    reference = models.CharField(
        max_length=150,
        blank=True, # La referencia es opcional, no siempre se tendrá una.
        verbose_name="referencia o código de transacción",
        help_text="Información adicional (Depósito de seguridad para extranjero, 50% del costo del alquiler, etc.)."
    )
    
    # --- Campos de Auditoría ---
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    class Meta:
        db_table = 'payment'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"Pago de ${self.amount})"
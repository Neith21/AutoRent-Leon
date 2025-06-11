import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from rental.models import Rental

def generate_invoice_number():
    """
    Genera un número de factura único basado en la fecha y un UUID corto.
    Ejemplo: INV-20240607-A4E1
    """
    date_str = timezone.now().strftime('%Y%m%d')
    unique_id = uuid.uuid4().hex.upper()[:4]
    return f"INV-{date_str}-{unique_id}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Emitida', 'Emitida'),
        ('Pagada', 'Pagada'),
        ('Anulada', 'Anulada'),
    ]

    rental = models.OneToOneField(
        Rental,
        on_delete=models.CASCADE, # Si se elimina el alquiler, se elimina su factura.
        verbose_name="alquiler asociado",
        help_text="El alquiler que genera esta factura.",
        error_messages={'required': "La factura debe estar asociada a un alquiler."}
    )
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        default=generate_invoice_number,
        verbose_name="número de factura",
        help_text="Código único de la factura. Se genera automáticamente.",
        error_messages={'unique': "Este número de factura ya existe."}
    )
    issue_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="fecha y hora de emisión",
        help_text="Momento en que se emite la factura."
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="monto total de la factura",
        help_text="El costo total facturado, incluyendo todos los cargos.",
        validators=[MinValueValidator(0.00)],
        error_messages={
            'required': "El monto total es obligatorio.",
            'invalid': "Ingrese un monto válido."
        }
    )
    reference = models.TextField(
        blank=True,
        verbose_name="referencia o código de transacción",
        help_text="Información adicional (Depósito de seguridad para extranjero, 50% del costo del alquiler, etc.)."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Emitida',
        verbose_name="estado de la factura",
        help_text="Estado actual de la factura (emitida, pagada, anulada)."
    )

    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.IntegerField(null=True, blank=True, verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    modified_by = models.IntegerField(null=True, blank=True, verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="última modificación")

    class Meta:
        db_table = 'invoice'
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-issue_date']

    def __str__(self):
        return f"Factura {self.invoice_number} - Alquiler #{self.rental.id}"

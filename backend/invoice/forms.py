from django import forms
from django.db.models import Sum
from .models import Invoice
from rental.models import Rental
from payment.models import Payment
from decimal import Decimal

class InvoiceCreateForm(forms.Form):
    
    rental_id = forms.IntegerField(
        error_messages={'required': 'El ID del alquiler es obligatorio.'}
    )
    payment_ids = forms.ModelMultipleChoiceField(
        queryset=Payment.objects.all(),
        error_messages={'required': 'Debe proporcionar una lista de IDs de pagos.',
                        'invalid_list': 'Debe proporcionar una lista de IDs de pagos válida.'}
    )
    status = forms.ChoiceField(
        choices=[('Emitida', 'Emitida'), ('Pagada', 'Pagada')],
        error_messages={'required': 'El estado de la factura es obligatorio.'}
    )

    def clean_rental_id(self):
        rental_id = self.cleaned_data.get('rental_id')
        try:
            rental = Rental.objects.get(pk=rental_id)
            if rental.status != 'Finalizado':
                raise forms.ValidationError("Solo se pueden generar facturas para alquileres con estado 'Finalizado'.")
            if Invoice.objects.filter(rental=rental).exists():
                raise forms.ValidationError(f"Ya existe una factura para el alquiler #{rental_id}.")
            return rental_id
        except Rental.DoesNotExist:
            raise forms.ValidationError(f"El alquiler con ID #{rental_id} no existe.")

    def clean(self):
        cleaned_data = super().clean()
        rental_id = cleaned_data.get('rental_id')
        payments = cleaned_data.get('payment_ids')

        if not rental_id or not payments:
            return cleaned_data

        for payment in payments:
            if payment.rental_id != rental_id:
                raise forms.ValidationError(f"El pago #{payment.id} no pertenece al alquiler #{rental_id}.")

        total = payments.aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal('0.00')
        
        reference_lines = []
        for p in payments.order_by('payment_date'):
            ref = p.reference if p.reference else p.concept
            reference_lines.append(f"- {ref}: ${p.amount}")
        
        cleaned_data['total_amount'] = total
        cleaned_data['reference_detail'] = "\n".join(reference_lines)
        
        return cleaned_data

class InvoiceStatusUpdateForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = ['status']
        error_messages = {
            'status': {
                'required': "El campo 'status' es obligatorio.",
                'invalid_choice': "El estado proporcionado no es válido. Opciones: Emitida, Pagada, Anulada."
            }
        }
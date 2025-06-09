from rest_framework import serializers
from rental.models import Rental
from django.contrib.auth.models import User
from django.db import transaction
import decimal
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum # Para la función Sum en aggregate
from payment.models import Payment 

class RentalSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Rental.

    Transforma las instancias de Rental a formato JSON. Incluye detalles
    de los modelos relacionados (Cliente, Vehículo, Sucursal) para una
    respuesta más completa y legible.
    """

    # --- Campos de Modelos Relacionados (para lectura) ---
    customer_name = serializers.CharField(source='customer.__str__', read_only=True) # Aquí podes ponerle source='customer.first_name' para obtener el nombre
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    pickup_branch_name = serializers.CharField(source='pickup_branch.name', read_only=True)
    return_branch_name = serializers.CharField(source='return_branch.name', read_only=True)

    # --- Campos de Auditoría Personalizados ---
    created_by_name = serializers.SerializerMethodField(read_only=True)
    modified_by_name = serializers.SerializerMethodField(read_only=True)

    # --- Formateo de Fechas (incluyendo hora) ---
    start_date = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M",
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
    )
    end_date = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M",
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
    )
    # actual_return_date también si lo vas a recibir en el mismo formato
    actual_return_date = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M",
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        read_only=False, # Si lo vas a recibir en la entrada
        allow_null=True
    )
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    class Meta:
        model = Rental
        fields = (
            "id",
            "customer", # ID del cliente
            "customer_name",
            "vehicle", # ID del vehículo
            "vehicle_plate",
            "pickup_branch", # ID de sucursal de recogida
            "pickup_branch_name",
            "return_branch", # ID de sucursal de devolución
            "return_branch_name",
            "start_date",
            "end_date",
            "actual_return_date",
            "status",
            "total_price",
            "fuel_level_pickup",
            "fuel_level_return",
            "remarks",
            "active",
            "created_by",
            "created_by_name",
            "created_at",
            "modified_by",
            "modified_by_name",
            "updated_at"
        )
    def get_created_by_name(self, obj):
        """
        Obtiene el 'first_name' del usuario que creó el alquiler.
        """
        if obj.created_by is None:
            return None
        try:
            user = User.objects.get(id=obj.created_by)
            return user.first_name
        except (User.DoesNotExist, ValueError):
            return None

    def get_modified_by_name(self, obj):
        """
        Obtiene el 'first_name' del usuario que modificó el alquiler por última vez.
        """
        if obj.modified_by is None:
            return None
        try:
            user = User.objects.get(id=obj.modified_by)
            return user.first_name
        except (User.DoesNotExist, ValueError):
            return None

    def validate(self, data):
        # Cuando se crea un alquiler, self.instance es None. En una actualización, es el objeto existente.
        is_creating = self.instance is None

        customer = data.get('customer')
        vehicle = data.get('vehicle')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # --- Validaciones Paso 3: Pre-cálculos y Validaciones (en creación) ---

        # 1. Cliente Existente y Activo
        if not customer:
            raise serializers.ValidationError({"customer": "Se requiere un cliente."})
        if customer.status == 'lista_negra':
            raise serializers.ValidationError({"customer": "El cliente está en la lista negra y no puede alquilar vehículos."})
        if not customer.active:
            raise serializers.ValidationError({"customer": "El cliente no está activo."})

        # 2. Fechas Válidas
        if not (start_date and end_date):
            raise serializers.ValidationError("Las fechas de inicio y fin son obligatorias.")
        if start_date < timezone.now() - timedelta(minutes=1):
            raise serializers.ValidationError({"start_date": "La fecha y hora de inicio no puede ser una fecha pasada."})
        if end_date <= start_date:
            raise serializers.ValidationError({"end_date": "La fecha y hora de fin debe ser posterior a la fecha de inicio."})

        # Calcular duración
        duration_days = (end_date.date() - start_date.date()).days + 1
        if duration_days <= 0:
            raise serializers.ValidationError({"dates": "La duración del alquiler debe ser al menos un día."})
        data['duration_days'] = duration_days # Almacenar para uso posterior

        # 3. Vehículo Disponible
        if not vehicle:
            raise serializers.ValidationError({"vehicle": "Se requiere un vehículo."})
        if not vehicle.active:
            raise serializers.ValidationError({"vehicle": "El vehículo no está activo."})
        # Verifica si el vehículo ya está alquilado para el período
        conflicting_rentals = Rental.objects.filter(
            vehicle=vehicle,
            end_date__gte=start_date,
            start_date__lte=end_date,
            status__in=['Activo', 'Reservado'],
            active=True
        )
        if self.instance: # Excluir el alquiler actual si estamos actualizando
            conflicting_rentals = conflicting_rentals.exclude(id=self.instance.id)

        if conflicting_rentals.exists():
            raise serializers.ValidationError({"vehicle": "El vehículo no está disponible para las fechas seleccionadas."})

        # Calcular total_price (basado en la tarifa diaria del vehículo)
        # Puedes mover esto al `create` si quieres que el `total_price` sea estrictamente determinado al guardar.
        # Pero para que el frontend pueda previsualizarlo, es útil aquí.
        data['total_price'] = vehicle.daily_rate * decimal.Decimal(str(duration_days))

        # 4. Límites de Vehículos Simultáneos por Cliente (Solo en creación)
        if is_creating:
            active_rentals_count = Rental.objects.filter(
                customer=customer,
                status__in=['Activo', 'Reservado'],
                active=True
            ).count()

            if customer.customer_type == 'nacional' and active_rentals_count >= 5:
                raise serializers.ValidationError({"customer": "Cliente nacional ya ha alcanzado el límite de 5 vehículos simultáneos."})
            elif customer.customer_type == 'extranjero' and active_rentals_count >= 3:
                raise serializers.ValidationError({"customer": "Cliente extranjero ya ha alcanzado el límite de 3 vehículos simultáneos."})

        # --- Validaciones Paso 4: Pagos Parciales y Depósitos (solo en creación) ---
        if is_creating:
            payments_data = data.get('payments', [])
            initial_payment_amount = decimal.Decimal('0.00')
            deposit_payment_exists = False
            
            for payment_data_item in payments_data:
                amount = payment_data_item.get('amount', decimal.Decimal('0.00'))
                concept = payment_data_item.get('concept')
                
                if concept in ['anticipo', 'pago_final']:
                    initial_payment_amount += amount
                if concept == 'deposito_garantia' and customer.customer_type == 'extranjero':
                    if amount >= decimal.Decimal('100.00'):
                        deposit_payment_exists = True
                    else:
                        raise serializers.ValidationError({"payments": "El depósito de garantía para extranjeros debe ser de al menos $100."})

            required_initial_payment_percentage = 0.50 if duration_days <= 5 else 1.00
            required_initial_amount = data['total_price'] * decimal.Decimal(str(required_initial_payment_percentage))
            
            if initial_payment_amount < required_initial_amount:
                raise serializers.ValidationError({
                    "payments": f"Se requiere un pago inicial de al menos ${required_initial_amount:.2f} (el {required_initial_payment_percentage*100:.0f}% del total)."
                })

            if customer.customer_type == 'extranjero' and not deposit_payment_exists:
                raise serializers.ValidationError({"payments": "Para clientes extranjeros se requiere un depósito de garantía de $100."})

        return data

    @transaction.atomic
    def create(self, validated_data):
        payments_data = validated_data.pop('payments', [])
        
        # Eliminar 'duration_days' ya que no es un campo del modelo Rental
        validated_data.pop('duration_days', None) 

        # Establecer el estado inicial del alquiler
        # Asume 'Reservado' por defecto según tu modelo, pero podrías cambiarlo a 'Activo'
        # si el pago inicial es el 100% aquí mismo.
        # Por simplicidad, lo dejamos como 'Reservado' y lo activa en un proceso posterior.
        # validated_data['status'] = 'Reservado' # Ya es el default en el modelo

        # Asignar total_price que ya fue calculado en validate()
        # Asegúrate de que el total_price se pasa explícitamente si no es parte de read_only_fields en Meta
        rental = Rental.objects.create(**validated_data)

        # Crear los pagos asociados al alquiler
        for payment_data_item in payments_data:
            # Asegúrate de que el payment_date se establece si no viene en la data
            if 'payment_date' not in payment_data_item:
                payment_data_item['payment_date'] = timezone.now()
            Payment.objects.create(rental=rental, **payment_data_item)

        # Marca el vehículo como no disponible
        rental.vehicle.is_available = False
        rental.vehicle.save()

        return rental



class RentalFinalizeSerializer(serializers.Serializer):
    """
    Serializador para la lógica de finalización de un alquiler.
    """
    actual_return_date = serializers.DateTimeField(required=True)
    fuel_level_return = serializers.CharField(max_length=10, required=True)
    remarks = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        rental = self.context.get('rental') # El objeto Rental pasado por el view
        if not rental:
            raise serializers.ValidationError("No se proporcionó un objeto Rental para finalizar.")

        actual_return_date = data.get('actual_return_date')
        fuel_level_return = data.get('fuel_level_return')

        # Validaciones de estado
        if rental.status == 'Finalizado': # Tu estado 'Finalizado'
            raise serializers.ValidationError("Este alquiler ya ha sido finalizado.")
        if rental.status == 'Cancelado': # Tu estado 'Cancelado'
            raise serializers.ValidationError("Este alquiler ha sido cancelado y no puede ser finalizado.")

        # Validación de fecha de devolución real
        if actual_return_date < rental.start_date:
            raise serializers.ValidationError({"actual_return_date": "La fecha de devolución real no puede ser anterior a la fecha de inicio del alquiler."})
        
        # Validación del nivel de combustible de retorno
        if fuel_level_return not in [choice[0] for choice in Rental.FUEL_LEVEL_CHOICES]:
            raise serializers.ValidationError({"fuel_level_return": "Nivel de combustible de retorno inválido."})

        return data

    @transaction.atomic
    def save(self, **kwargs):
        rental = self.context['rental']
        actual_return_date = self.validated_data['actual_return_date']
        fuel_level_return = self.validated_data['fuel_level_return']
        remarks = self.validated_data.get('remarks')

        # Actualizar los campos del alquiler
        rental.actual_return_date = actual_return_date
        rental.fuel_level_return = fuel_level_return
        rental.remarks = remarks

        # 1. Calcular Recargos por Retraso
        overdue_charge = decimal.Decimal('0.00')
        days_overdue = 0

        # Convertir a objetos date para cálculo de días completos de retraso
        if actual_return_date.date() > rental.end_date.date():
            days_overdue = (actual_return_date.date() - rental.end_date.date()).days

            daily_rate = rental.vehicle.daily_rate # Obtener la tarifa diaria del vehículo

            if days_overdue <= 3:
                overdue_charge = daily_rate * days_overdue
            elif days_overdue <= 7:
                # Los primeros 3 días a tarifa normal, los siguientes 4 a tarifa doble.
                overdue_charge = (daily_rate * 3) + (daily_rate * 2 * (days_overdue - 3))
            else:
                # Más de 7 días: 3 normal, 4 doble, y el resto triple (o como definas 'más de 7 días')
                overdue_charge = (daily_rate * 3) + (daily_rate * 2 * 4) + (daily_rate * 3 * (days_overdue - 7))
                print(f"ALERTA: Alquiler {rental.id} retrasado más de 7 días. Notificar a la policía.")
                # Considera un campo en Rental para marcar esto, o un sistema de logging/alertas.
                # rental.police_notified = True # Ejemplo, si tuvieras este campo

            # Añadir el recargo al precio total del alquiler
            rental.total_price += overdue_charge
            rental.status = 'Retrasado' if days_overdue > 0 else 'Finalizado' # Tus estados

        # 2. Verificar Pagos Pendientes
        # Sumar todos los pagos que son 'anticipo', 'pago_final', 'cargo_adicional'
        total_paid = Payment.objects.filter(
            rental=rental,
            concept__in=['anticipo', 'pago_final', 'cargo_adicional']
        ).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')
        
        remaining_balance = rental.total_price - total_paid

        # Gestión del depósito de garantía
        if rental.customer.customer_type == 'extranjero':
            # Suma de todos los depósitos de garantía recibidos para este alquiler
            deposit_received = Payment.objects.filter(
                rental=rental,
                concept='deposito_garantia'
            ).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')
            
            # Si hay un depósito y el cliente no tiene saldo pendiente o incluso sobrepagó
            if deposit_received > 0 and remaining_balance <= 0:
                # Generar un registro de devolución de depósito
                # Aquí puedes decidir si el monto a devolver es el depósito original
                # o el remanente si hubo algún cargo que no fue cubierto por pagos normales.
                # Para simplicidad, se devuelve el depósito original si no hay saldo pendiente.
                
                # Check if a return deposit payment already exists to prevent duplicates
                if not Payment.objects.filter(rental=rental, concept='devolucion_deposito').exists():
                    Payment.objects.create(
                        rental=rental,
                        amount=deposit_received, # Registra el monto original del depósito como devuelto
                        payment_type='efectivo', # O un tipo específico para reembolsos
                        payment_date=timezone.now(),
                        concept='devolucion_deposito',
                        reference=f"Devolución Depósito Alquiler {rental.id}"
                    )
                print(f"Depósito de garantía de ${deposit_received:.2f} devuelto para alquiler {rental.id}.")


        if remaining_balance > decimal.Decimal('0.00'):
            # Lanza una excepción para que el view la capture y devuelva un error 400
            raise serializers.ValidationError({
                "payment_required": f"Quedan ${remaining_balance:.2f} pendientes. Por favor, registre el pago final."
            })
        elif remaining_balance < decimal.Decimal('0.00'):
            # Si el cliente sobrepagó (ej. por un error, o un reembolso manual que aún no se registró)
            print(f"Alquiler {rental.id} sobrepagado por ${abs(remaining_balance):.2f}. Considerar reembolso adicional.")
            # Podrías crear otro 'reembolso' aquí para cuadrar la cuenta.

        # 3. Generar Factura (si no existe y todo está pagado)
        if not hasattr(rental, 'invoice') and remaining_balance <= decimal.Decimal('0.00'):
            # Generar número de factura secuencial
            latest_invoice = Invoice.objects.order_by('-id').first()
            if latest_invoice and latest_invoice.invoice_number.startswith('INV'):
                try:
                    last_num = int(latest_invoice.invoice_number[3:])
                    new_invoice_number = f"INV{last_num + 1:05d}"
                except ValueError: # En caso de que el formato no sea el esperado
                    new_invoice_number = f"INV{Invoice.objects.count() + 1:05d}"
            else:
                new_invoice_number = "INV00001"

            Invoice.objects.create(
                rental=rental,
                invoice_number=new_invoice_number,
                issue_date=timezone.now(),
                total_amount=rental.total_price,
                status='emitida',
                created_by=kwargs.get('modified_by', None) # Quien finaliza es el que 'crea' la factura aquí
            )
            print(f"Factura {new_invoice_number} emitida para alquiler {rental.id}.")
        elif hasattr(rental, 'invoice') and remaining_balance <= decimal.Decimal('0.00') and rental.invoice.status != 'pagada':
             # Si ya existe una factura pero no está pagada y ahora sí se completaron los pagos
             rental.invoice.status = 'pagada'
             rental.invoice.modified_by = kwargs.get('modified_by', None)
             rental.invoice.save()


        # Actualizar el estado del vehículo a disponible
        rental.vehicle.is_available = True
        rental.vehicle.save()

        # Guardar los cambios en el alquiler
        rental.save(modified_by=kwargs.get('modified_by', None)) # Asegurar que `modified_by` se guarda

        return rental
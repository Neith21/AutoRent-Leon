from rest_framework import serializers
from rental.models import Rental
from django.contrib.auth.models import User
from django.db import transaction
import decimal
import math
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from payment.models import Payment
from payment.serializers import PaymentSerializer as NestedPaymentSerializer
from customer.models import Customer
from vehicle.models import Vehicle

# Intenta importar el modelo Invoice. Si no existe, se establece como None.
try:
    from invoice.models import Invoice
except ImportError:
    Invoice = None 


# --- NestedPaymentSerializer (Asegúrate de que este serializer exista y sea correcto) ---
class NestedPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_type = serializers.CharField(max_length=50) # El max_length es importante aquí
    concept = serializers.CharField(max_length=100, required=False) # Será asignado por el backend en create/update
    reference = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)


# --- RentalSerializer Principal con los Cambios (Este no lo modificamos ahora) ---
class RentalSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Rental.
    """

    customer_name = serializers.CharField(source='customer.__str__', read_only=True)
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    pickup_branch_name = serializers.CharField(source='pickup_branch.name', read_only=True)
    return_branch_name = serializers.CharField(source='return_branch.name', read_only=True)

    # Nuevos campos read_only del vehículo
    vehicle_daily_price = serializers.DecimalField(source='vehicle.daily_price', max_digits=10, decimal_places=2, read_only=True)
    vehicle_make = serializers.CharField(source='vehicle.make', read_only=True)
    vehicle_model = serializers.CharField(source='vehicle.model', read_only=True)
    
    created_by_name = serializers.SerializerMethodField(read_only=True)
    modified_by_name = serializers.SerializerMethodField(read_only=True)

    start_date = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M",
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        default_timezone=timezone.get_current_timezone()
    )
    end_date = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M",
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        required=False,
        allow_null=True, # Puede ser nulo para alquileres abiertos
        default_timezone=timezone.get_current_timezone()
    )
    actual_return_date = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M",
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        required=False,
        allow_null=True,
        default_timezone=timezone.get_current_timezone()
    )
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    # Campo para la ENTRADA de pagos (cuando creas una renta)
    payments_input = NestedPaymentSerializer(many=True, required=False, write_only=True)
    # Campo para la SALIDA de pagos (cuando lees una renta existente)
    payments = NestedPaymentSerializer(many=True, required=False, read_only=True, source='payment_set')

    class Meta:
        model = Rental
        fields = (
            "id",
            "customer",
            "customer_name",
            "vehicle",
            "vehicle_plate",
            # Nuevos campos del vehículo
            "vehicle_daily_price",
            "vehicle_make",
            "vehicle_model",
            # Fin nuevos campos del vehículo
            "pickup_branch",
            "pickup_branch_name",
            "return_branch",
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
            "updated_at",
            "payments",      # Asegúrate de que 'payments' (lectura) esté en los 'fields'
            "payments_input", # Asegúrate de que 'payments_input' (escritura) esté en los 'fields'
        )
        extra_kwargs = {
            'status': {'required': False}
        }

    def get_created_by_name(self, obj):
        if obj.created_by is None:
            return None
        try:
            # Asegúrate de que User esté correctamente importado o usa get_user_model()
            user = User.objects.get(id=obj.created_by)
            return user.first_name if user.first_name else user.username
        except (User.DoesNotExist, ValueError):
            return None

    def get_modified_by_name(self, obj):
        if obj.modified_by is None:
            return None
        try:
            # Asegúrate de que User esté correctamente importado o usa get_user_model()
            user = User.objects.get(id=obj.modified_by)
            return user.first_name if user.first_name else user.username
        except (User.DoesNotExist, ValueError):
            return None

    def validate(self, data):
        is_creating = self.instance is None

        customer = data.get('customer')
        vehicle = data.get('vehicle')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        # NOTA IMPORTANTE: Ahora obtenemos los datos de pagos desde 'payments_input' para la validación de entrada
        payments_data = data.get('payments_input', [])

        # --- Validaciones de Cliente ---
        if not customer:
            raise serializers.ValidationError({"customer": "Se requiere un cliente."})
        if customer.status == 'lista_negra':
            raise serializers.ValidationError({"customer": "El cliente está en la lista negra y no puede alquilar vehículos."})
        if not customer.active:
            raise serializers.ValidationError({"customer": "El cliente no está activo."})

        # --- Validaciones de Fechas ---
        if not (start_date and end_date):
            raise serializers.ValidationError("Las fechas de inicio y fin son obligatorias.")

        # Comentar o ajustar esto si quieres permitir crear rentas en el pasado para fines de registro
        # if start_date < timezone.now() - timedelta(minutes=1):
        #     raise serializers.ValidationError({"start_date": "La fecha y hora de inicio no puede ser una fecha pasada."})
        
        if end_date <= start_date:
            raise serializers.ValidationError({"end_date": "La fecha y hora de fin debe ser posterior a la fecha de inicio."})

        duration_days = (end_date.date() - start_date.date()).days
        # Ajuste para incluir el día de finalización si excede la hora de inicio o si es el mismo día con duración
        if start_date.date() != end_date.date() and (end_date.hour > start_date.hour or (end_date.hour == start_date.hour and end_date.minute > start_date.minute)):
            duration_days += 1
        elif start_date.date() == end_date.date() and (end_date.total_seconds() - start_date.total_seconds() > 0):
            duration_days = 1

        if duration_days <= 0:
            raise serializers.ValidationError({"dates": "La duración del alquiler debe ser al menos un día."})
        data['duration_days'] = duration_days

        # --- Validaciones de Vehículo ---
        if not vehicle:
            raise serializers.ValidationError({"vehicle": "Se requiere un vehículo."})
        if not vehicle.active:
            raise serializers.ValidationError({"vehicle": "El vehículo no está activo."})

        # Conflicto de rentas existentes
        conflicting_rentals = Rental.objects.filter(
            vehicle=vehicle,
            end_date__gte=start_date,
            start_date__lte=end_date,
            status__in=['Activo', 'Reservado'],
            active=True
        )
        if self.instance:
            conflicting_rentals = conflicting_rentals.exclude(id=self.instance.id)

        if conflicting_rentals.exists():
            raise serializers.ValidationError({"vehicle": "El vehículo no está disponible para las fechas seleccionadas debido a un alquiler existente."})

        # --- Cálculo del Precio Total de la Renta ---
        total_rental_price = vehicle.daily_price * decimal.Decimal(str(duration_days))
        data['total_price'] = total_rental_price.quantize(decimal.Decimal('0.01'))


        # ***************************************************************
        # Lógica de Validación y Asignación de Conceptos de Pago
        # ***************************************************************

        # Definir el porcentaje de pago inicial del alquiler
        required_rental_payment_percentage = decimal.Decimal('0.50')
        if duration_days > 5:
            required_rental_payment_percentage = decimal.Decimal('1.00')

        # Calcular el monto del anticipo del alquiler (sin depósito)
        required_rental_payment_amount = (total_rental_price * required_rental_payment_percentage).quantize(decimal.Decimal('0.01'))

        # Calcular el depósito requerido para extranjeros
        deposit_required = decimal.Decimal('0.00')
        if customer.customer_type.lower() == 'extranjero':
            deposit_required = decimal.Decimal('100.00')

        # Monto total EXACTO que se espera de pago inicial (anticipo + depósito)
        expected_total_initial_payment = (required_rental_payment_amount + deposit_required).quantize(decimal.Decimal('0.01'))

        if is_creating:
            if not payments_data:
                raise serializers.ValidationError({"payments_input": "Se requiere al menos un pago inicial para crear esta renta."})

            actual_initial_payment_sum = decimal.Decimal('0.00')
            for p_data in payments_data:
                # Validar cada pago individualmente
                payment_serializer = NestedPaymentSerializer(data=p_data)
                payment_serializer.is_valid(raise_exception=True)
                actual_initial_payment_sum += decimal.Decimal(str(p_data['amount'])).quantize(decimal.Decimal('0.01'))

            if actual_initial_payment_sum != expected_total_initial_payment:
                raise serializers.ValidationError(
                    {"payments_input": f"El monto total del pago inicial ({actual_initial_payment_sum}) debe ser exactamente {expected_total_initial_payment}."}
                )

            # Ya no es necesario asignar `concept` aquí porque la lógica `create` lo hará.
            # Solo necesitamos asegurarnos de que el `payments_input` sea el que se pasa.
            # La validación ya ocurrió en el `actual_initial_payment_sum`

        # --- Límites de Vehículos Simultáneos por Cliente (Solo en creación) ---
        if is_creating:
            active_rentals_count = Rental.objects.filter(
                customer=customer,
                status__in=['Activo', 'Reservado'],
                active=True
            ).count()

            if customer.customer_type == 'nacional' and active_rentals_count >= 5:
                raise serializers.ValidationError({"customer": f"Cliente nacional ya ha alcanzado el límite de {active_rentals_count} de 5 vehículos simultáneos."})
            elif customer.customer_type.lower() == 'extranjero' and active_rentals_count >= 3:
                raise serializers.ValidationError({"customer": f"Cliente extranjero ya ha alcanzado el límite de {active_rentals_count} de 3 vehículos simultáneos."})

        return data

    @transaction.atomic
    def create(self, validated_data):
        # Extraer los datos de pagos de 'payments_input' para procesarlos por separado
        initial_payment_data = validated_data.pop('payments_input', [])
        validated_data.pop('duration_days', None) # Asegúrate de que no se intente guardar este campo en el modelo

        request = self.context.get('request')
        user_id = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id
            validated_data['created_by'] = user_id
            validated_data['modified_by'] = user_id

        rental = Rental.objects.create(**validated_data)

        # Recalcular los montos esperados (anticipo y depósito) con los datos del rental recién creado
        # Esto es importante para asegurar que estamos creando los pagos con los montos validados por el backend
        customer = rental.customer
        vehicle = rental.vehicle
        start_date = rental.start_date
        end_date = rental.end_date

        duration_days = (end_date.date() - start_date.date()).days
        if start_date.date() != end_date.date() and (end_date.hour > start_date.hour or (end_date.hour == start_date.hour and end_date.minute > start_date.minute)):
            duration_days += 1
        elif start_date.date() == end_date.date() and (end_date.total_seconds() - start_date.total_seconds() > 0):
            duration_days = 1
            
        total_rental_price = (vehicle.daily_price * decimal.Decimal(str(duration_days))).quantize(decimal.Decimal('0.01'))

        required_rental_payment_percentage = decimal.Decimal('0.50')
        if duration_days > 5:
            required_rental_payment_percentage = decimal.Decimal('1.00')

        required_rental_payment_amount = (total_rental_price * required_rental_payment_percentage).quantize(decimal.Decimal('0.01'))
        deposit_required = decimal.Decimal('0.00')
        if customer.customer_type.lower() == 'extranjero':
            deposit_required = decimal.Decimal('100.00')

        # Si viene un solo pago del frontend que suma anticipo + depósito (lo más común)
        # Asumimos que `initial_payment_data` contiene el monto total recibido.
        # Creamos dos objetos `Payment` si es necesario.
        if initial_payment_data:
            payment_info = initial_payment_data[0] # Asumimos que es un solo objeto de pago inicial
            initial_payment_type = payment_info.get('payment_type', 'Efectivo')
            initial_payment_reference = payment_info.get('reference', None)

            # 1. Crear el pago para el anticipo del alquiler
            if required_rental_payment_amount > decimal.Decimal('0.00'):
                payment_concept = 'Anticipo'
                if required_rental_payment_percentage == decimal.Decimal('1.00'):
                    payment_concept = 'Pago Final'

                Payment.objects.create(
                    rental=rental,
                    amount=required_rental_payment_amount,
                    payment_type=initial_payment_type,
                    concept=payment_concept,
                    reference=initial_payment_reference if initial_payment_reference else f"{payment_concept} Renta #{rental.id}",
                    payment_date=timezone.now(),
                    created_by=user_id,
                    modified_by=user_id
                )

            # 2. Crear el pago para el depósito de garantía si aplica
            if deposit_required > decimal.Decimal('0.00'):
                Payment.objects.create(
                    rental=rental,
                    amount=deposit_required,
                    payment_type=initial_payment_type,
                    concept='Depósito',
                    reference=f"Depósito de garantía Renta #{rental.id}",
                    payment_date=timezone.now(),
                    created_by=user_id,
                    modified_by=user_id
                )

        vehicle = rental.vehicle
        if rental.status == 'Activo':
            vehicle.status = 'Alquilado'
        elif rental.status == 'Reservado':
            vehicle.status = 'Reservado'
        vehicle.save()

        return rental

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['modified_by'] = request.user.id

        # No permitir actualizar pagos directamente desde el update de Rental
        validated_data.pop('payments_input', None) 
        validated_data.pop('duration_days', None) 

        return super().update(instance, validated_data)


# --- RentalFinalizeSerializer (con las correcciones aplicadas) ---
class RentalFinalizeSerializer(serializers.Serializer):
    rental_id = serializers.IntegerField(read_only=True)
    actual_return_date = serializers.DateTimeField(
        required=True,
        format="%Y-%m-%dT%H:%M",
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        default_timezone=timezone.get_current_timezone()
    )
    fuel_level_return = serializers.ChoiceField(
        choices=Rental.FUEL_LEVEL_CHOICES,
        required=True
    )
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    # final_payment es un solo NestedPaymentSerializer (no many=True)
    final_payment = NestedPaymentSerializer(required=False, allow_null=True)


    def validate(self, data):
        rental = self.context.get('rental')
        if not rental:
            raise serializers.ValidationError("No se proporcionó un objeto Rental para finalizar.")
        
        self.instance = rental
        data['rental_id'] = rental.id

        actual_return_date = data.get('actual_return_date')
        fuel_level_return = data.get('fuel_level_return')
        final_payment_data = data.get('final_payment')

        # 1. Validar el estado actual de la renta
        if rental.status == 'Finalizado':
            raise serializers.ValidationError({"status": "Este alquiler ya ha sido finalizado."})
        if rental.status == 'Cancelado':
            raise serializers.ValidationError({"status": "Este alquiler ha sido cancelado y no puede ser finalizado."})
        if rental.status == 'Pendiente':
            raise serializers.ValidationError({"status": "Este alquiler está Pendiente. No se puede finalizar hasta que esté Activo o Reservado."})

        # 2. Validar actual_return_date
        if actual_return_date < rental.start_date:
            raise serializers.ValidationError({"actual_return_date": "La fecha de devolución real no puede ser anterior a la fecha de inicio del alquiler."})
        
        # Pequeño margen para evitar problemas de microsegundos al comparar con now()
        if actual_return_date > timezone.now() + timedelta(minutes=1):
            raise serializers.ValidationError({"actual_return_date": "La fecha de devolución real no puede ser una fecha futura."})

        # 3. Calcular Recargos y Cargos por Combustible
        fuel_level_map = {choice[0]: i for i, choice in enumerate(Rental.FUEL_LEVEL_CHOICES)}
        pickup_level = fuel_level_map.get(rental.fuel_level_pickup, 0)
        return_level = fuel_level_map.get(fuel_level_return, 0)

        fuel_charge = decimal.Decimal('0.00')
        FUEL_COST_PER_LEVEL = decimal.Decimal('15.00') # Costo por nivel de combustible faltante

        # Se aplica cargo por combustible si el nivel de retorno es menor que el de recogida
        if return_level < pickup_level:
            fuel_charge = (pickup_level - return_level) * FUEL_COST_PER_LEVEL
        
        data['calculated_fuel_charge'] = fuel_charge.quantize(decimal.Decimal('0.01'))

        overdue_charge = decimal.Decimal('0.00')
        days_overdue = 0
        
        # Lógica de cargo por retraso: ¡Ajustada para que sea idéntica al frontend!
        # Si la fecha de retorno real es posterior a la fecha de finalización esperada
        if actual_return_date > rental.end_date:
            # Calcular la diferencia en horas y luego en días, redondeando hacia arriba para cualquier fracción de día
            diff_hours = (actual_return_date - rental.end_date).total_seconds() / (60 * 60)
            raw_days_overdue = math.ceil(diff_hours / 24)

            # Asegurar que incluso un retraso de pocas horas se cuente como 1 día
            if raw_days_overdue <= 0 and diff_hours > 0:
                raw_days_overdue = 1

            days_overdue = raw_days_overdue # Guardamos los días reales de retraso

            daily_price = rental.vehicle.daily_price

            if days_overdue <= 3:
                # Días 1 a 3: Tarifa diaria normal por cada día
                overdue_charge = daily_price * days_overdue
            elif days_overdue > 3 and days_overdue <= 7:
                # Días 4 a 7: Doble de la tarifa diaria por cada día en este rango
                overdue_charge = daily_price * days_overdue * 2
            else: # Más de 7 días de retraso: el cargo se mantiene como si fueran 7 días (con tarifa doble)
                overdue_charge = daily_price * 7 * 2
        
        data['calculated_overdue_charge'] = overdue_charge.quantize(decimal.Decimal('0.01'))
        data['days_overdue'] = days_overdue # Los días reales de retraso

        # Recalculamos el costo original de la renta sin el depósito para asegurar la base correcta.
        # Esto considera la duración original de la renta para el cálculo base.
        rental_duration_days_initial = (rental.end_date.date() - rental.start_date.date()).days
        if rental.start_date.date() != rental.end_date.date() and (rental.end_date.hour > rental.start_date.hour or (rental.end_date.hour == rental.start_date.hour and rental.end_date.minute > rental.start_date.minute)):
            rental_duration_days_initial += 1
        elif rental.start_date.date() == rental.end_date.date() and (rental.end_date.total_seconds() - rental.start_date.total_seconds() > 0):
            rental_duration_days_initial = 1
        
        total_original_rental_cost = (rental.vehicle.daily_price * decimal.Decimal(str(rental_duration_days_initial))).quantize(decimal.Decimal('0.01'))

        # total_amount_to_cover es el monto que el cliente *debe* por el servicio de alquiler y penalidades
        total_amount_to_cover = (total_original_rental_cost + overdue_charge + fuel_charge).quantize(decimal.Decimal('0.01'))

        # Monto total de pagos recibidos HASTA AHORA (sin el pago final de esta solicitud)
        # Filtrar solo los pagos que corresponden al servicio de alquiler, NO los depósitos.
        paid_for_rental_only = Payment.objects.filter(
            rental=rental,
            concept__in=['Anticipo', 'Pago Final', 'Cargo Adicional', 'Cargo por Retraso']
        ).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')

        # Verificar si ya se recibió un depósito de garantía para este alquiler (solo para extranjeros)
        deposit_received_amount = decimal.Decimal('0.00')
        # Buscar SÓLO pagos con concepto 'Depósito'
        deposit_payment = Payment.objects.filter(rental=rental, concept='Depósito').first()
        if deposit_payment:
            deposit_received_amount = deposit_payment.amount

        # Monto del pago que se está realizando en esta solicitud de finalización
        current_payment_in_request = final_payment_data.get('amount', decimal.Decimal('0.00')) if final_payment_data else decimal.Decimal('0.00')
        
        # Total pagado por el cliente *solo por el servicio de alquiler y cargos*, incluyendo el pago actual
        total_paid_by_customer_for_service = (paid_for_rental_only + current_payment_in_request).quantize(decimal.Decimal('0.01'))
        
        # Saldo pendiente real (lo que debe por el servicio - lo que ha pagado por el servicio)
        remaining_balance_for_service = (total_amount_to_cover - total_paid_by_customer_for_service).quantize(decimal.Decimal('0.01'))

        # Validar si el pago final es insuficiente si hay un saldo pendiente positivo
        if remaining_balance_for_service > decimal.Decimal('0.00'):
            # El pago actual debe cubrir al menos el saldo pendiente si se envía un pago
            # O si no se envía un pago, y hay saldo pendiente, entonces es un error
            if not final_payment_data or current_payment_in_request < remaining_balance_for_service:
                raise serializers.ValidationError({
                    "final_payment": f"El monto del pago es insuficiente. Quedan ${remaining_balance_for_service:.2f} pendientes por el servicio de alquiler y cargos. Por favor, ajuste el pago final."
                })
        
        # Si hay sobrepago o balance negativo, el sistema ahora debe calcular el reembolso.
        # Esto incluye cualquier sobrepago del servicio MÁS el depósito de garantía si aplica.
        total_refund_amount = decimal.Decimal('0.00')
        if remaining_balance_for_service < decimal.Decimal('0.00'):
            total_refund_amount += abs(remaining_balance_for_service) # Sobrepago del servicio

        # El depósito de garantía SIEMPRE se suma al reembolso si el servicio está cubierto.
        # Es decir, si el remaining_balance_for_service es cero o negativo (ya no se debe nada por el servicio).
        # Y solo si el depósito realmente se recibió
        if deposit_received_amount > decimal.Decimal('0.00') and remaining_balance_for_service <= decimal.Decimal('0.00'):
            total_refund_amount += deposit_received_amount 

        data['total_amount_to_cover'] = total_amount_to_cover
        data['total_paid_by_customer_for_service'] = total_paid_by_customer_for_service
        data['remaining_balance_for_service'] = remaining_balance_for_service
        data['deposit_received_amount'] = deposit_received_amount # Añadir esto para mostrar en el frontend si es necesario
        data['total_refund_amount'] = total_refund_amount.quantize(decimal.Decimal('0.01')) # Asegura el formato decimal

        return data

    @transaction.atomic
    def save(self, **kwargs):
        rental = self.instance
        actual_return_date = self.validated_data['actual_return_date']
        fuel_level_return = self.validated_data['fuel_level_return']
        remarks = self.validated_data.get('remarks')
        final_payment_data = self.validated_data.get('final_payment')

        calculated_overdue_charge = self.validated_data['calculated_overdue_charge']
        calculated_fuel_charge = self.validated_data['calculated_fuel_charge']
        total_amount_to_cover = self.validated_data['total_amount_to_cover']
        total_refund_amount = self.validated_data['total_refund_amount'] 
        remaining_balance_for_service = self.validated_data['remaining_balance_for_service']
        deposit_received_amount = self.validated_data['deposit_received_amount'] # Recuperar el monto del depósito

        user_id = kwargs.get('modified_by', None)
        if user_id:
            rental.modified_by = user_id

        # 1. Actualizar campos de la renta
        rental.actual_return_date = actual_return_date
        rental.fuel_level_return = fuel_level_return
        rental.remarks = remarks
        
        # El total_price del alquiler en el modelo debe reflejar el costo real de la renta más cargos.
        rental.total_price = total_amount_to_cover

        # Determinar el payment_type base para los nuevos registros de pagos/cargos
        # Si viene un final_payment, usar su tipo. Si no, un valor por defecto (ej. 'Efectivo')
        base_payment_type = final_payment_data.get('payment_type', 'Efectivo') if final_payment_data else 'Efectivo'

        # 2. Registrar el pago final si se envió y hay un monto y es necesario
        # Se registra un pago final SÓLO si el saldo restante para el servicio es positivo y el pago lo cubre
        # o si el pago recibido en esta transacción es positivo y no se ha cubierto el servicio aún.
        if final_payment_data and final_payment_data.get('amount', 0) > 0 and remaining_balance_for_service > decimal.Decimal('0.00'):
            # Evitar duplicar el "Pago Final"
            if not Payment.objects.filter(
                rental=rental,
                concept='Pago Final',
                amount=final_payment_data['amount'],
                payment_type=final_payment_data.get('payment_type', 'Efectivo')
            ).exists():
                Payment.objects.create(
                    rental=rental,
                    amount=final_payment_data['amount'],
                    payment_type=final_payment_data.get('payment_type', 'Efectivo'),
                    concept='Pago Final',
                    reference=final_payment_data.get('reference', f"Pago final Renta #{rental.id}"),
                    payment_date=timezone.now(),
                    created_by=user_id,
                    modified_by=user_id
                )

        # 3. Manejo de cargos adicionales por mora y combustible
        # Estos se registran como pagos para reflejar los montos que el cliente debe/pagó por estos conceptos.
        # Usaremos el base_payment_type para estos registros.
        if calculated_overdue_charge > 0:
            # Si ya existe un pago por este concepto y monto exacto, no crear duplicado.
            # Esto previene errores en reintentos.
            if not Payment.objects.filter(
                rental=rental, 
                concept='Cargo por Retraso', 
                amount=calculated_overdue_charge,
                payment_type=base_payment_type # Importante: Usar el tipo de pago del frontend
            ).exists():
                Payment.objects.create(
                    rental=rental,
                    amount=calculated_overdue_charge,
                    payment_type=base_payment_type, # Se usa el tipo de pago proporcionado por el frontend
                    concept='Cargo por Retraso',
                    reference=f"Recargo por demora Renta #{rental.id}",
                    payment_date=timezone.now(),
                    created_by=user_id,
                    modified_by=user_id
                )
        
        if calculated_fuel_charge > 0:
            # Si ya existe un pago por este concepto y monto exacto, no crear duplicado.
            if not Payment.objects.filter(
                rental=rental, 
                concept='Cargo Adicional', 
                amount=calculated_fuel_charge,
                payment_type=base_payment_type # Importante: Usar el tipo de pago del frontend
            ).exists():
                Payment.objects.create(
                    rental=rental,
                    amount=calculated_fuel_charge,
                    payment_type=base_payment_type, # Se usa el tipo de pago proporcionado por el frontend
                    concept='Cargo Adicional', # Usando 'Cargo Adicional' para combustible
                    reference=f"Cargo por combustible Renta #{rental.id}",
                    payment_date=timezone.now(),
                    created_by=user_id,
                    modified_by=user_id
                )

        # 4. Manejo del reembolso (si el `total_refund_amount` es mayor a 0)
        if total_refund_amount > decimal.Decimal('0.00'):
            refund_concept = 'Reembolso'
            refund_reference = f"Reembolso Alquiler #{rental.id}"
            
            is_foreigner = rental.customer.customer_type.lower() == 'extranjero'
            if is_foreigner and deposit_received_amount == decimal.Decimal('100.00') and total_refund_amount >= decimal.Decimal('100.00'):
                refund_concept = 'Reembolso de Depósito Extranjero'
                refund_reference = f"Reembolso de Depósito Extranjero Renta #{rental.id}"
            elif deposit_received_amount > decimal.Decimal('0.00'):
                refund_concept = 'Reembolso de Depósito'
                refund_reference = f"Reembolso de Depósito Renta #{rental.id}"

            # Verifica si ya se hizo un reembolso con el mismo monto y concepto para evitar duplicados.
            if not Payment.objects.filter(
                rental=rental,
                concept=refund_concept,
                amount=total_refund_amount * -1 # Se verifica el monto negativo
            ).exists(): 
                Payment.objects.create(
                    rental=rental,
                    amount=total_refund_amount * -1, # Monto negativo para indicar reembolso
                    payment_type=base_payment_type, # Se usa el tipo de pago proporcionado por el frontend
                    payment_date=timezone.now(),
                    concept=refund_concept,
                    reference=refund_reference,
                    created_by=user_id,
                    modified_by=user_id
                )

        # 5. Actualizar el estado de la renta a 'Finalizado'
        rental.status = 'Finalizado'

        # 6. Actualizar el estado del vehículo
        rental.vehicle.status = 'Disponible'
        rental.vehicle.save()

        rental.save()

        # 7. Manejo de Factura (si el modelo Invoice existe y el saldo está cubierto)
        if Invoice: # Verifica si la clase Invoice se importó correctamente
            try:
                # Si no hay factura asociada y el balance es cero o negativo (cubierto)
                if not hasattr(rental, 'invoice') and remaining_balance_for_service <= decimal.Decimal('0.00'):
                    latest_invoice = Invoice.objects.order_by('-id').first()
                    new_invoice_number = "INV00001"
                    if latest_invoice and latest_invoice.invoice_number.startswith('INV'):
                        try:
                            last_num = int(latest_invoice.invoice_number[3:])
                            new_invoice_number = f"INV{last_num + 1:05d}"
                        except ValueError:
                            # Fallback si el número no es el formato esperado
                            new_invoice_number = f"INV{Invoice.objects.count() + 1:05d}"
                    
                    Invoice.objects.create(
                        rental=rental,
                        invoice_number=new_invoice_number,
                        issue_date=timezone.now(),
                        total_amount=rental.total_price, # Usar el total_price ya actualizado con cargos
                        status='emitida',
                        created_by=user_id
                    )
                # Si ya hay una factura y el balance es cero o negativo, y la factura no está pagada, actualizarla a 'pagada'
                elif hasattr(rental, 'invoice') and remaining_balance_for_service <= decimal.Decimal('0.00') and rental.invoice.status != 'pagada':
                    rental.invoice.status = 'pagada'
                    rental.invoice.modified_by = user_id
                    rental.invoice.save()
            except Exception as e:
                # Captura cualquier error en la creación/actualización de la factura
                print(f"Error al manejar la factura para la renta {rental.id}: {e}")

                pass # Se mantiene el `pass` para que no detenga la transacción principal
        return rental
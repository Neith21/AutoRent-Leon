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
from payment.serializers import PaymentSerializer as NestedPaymentSerializer # Asegúrate de que esta línea esté correcta
from customer.models import Customer
from vehicle.models import Vehicle
import pytz

# --- NestedPaymentSerializer (Asegúrate de que este serializer exista y sea correcto) ---
class NestedPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_type = serializers.CharField(max_length=50) # El max_length es importante aquí
    concept = serializers.CharField(max_length=100, required=False) # Será asignado por el backend en create/update
    reference = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)

    # AÑADIDO: Método create() para la creación de pagos
    def create(self, validated_data):
        # La vista RentalAddPaymentAPIView pasa 'rental' y 'created_by'
        # directamente a serializer.save() como argumentos.
        # Estos argumentos se convierten en 'kwargs' para el método create().
        # No están en 'validated_data' directamente, por eso los sacamos de kwargs.

        # Extraer los argumentos adicionales que no son parte de los campos del serializer
        # Usamos .pop() para removerlos de validated_data y evitar errores al crear el Payment.
        rental = validated_data.pop('rental') 
        created_by = validated_data.pop('created_by', None) 

        # Crear el objeto Payment
        payment = Payment.objects.create(
            rental=rental,
            amount=validated_data['amount'],
            payment_type=validated_data['payment_type'],
            concept=validated_data.get('concept', 'Pago'), 
            reference=validated_data.get('reference', None),
            payment_date=timezone.now(), 
            created_by=created_by,
            modified_by=created_by 
        )
        return payment

    # AÑADIDO: Método update() (vacío por ahora, pero necesario si luego quieres actualizar pagos)
    def update(self, instance, validated_data):
        # Generalmente, no se "actualizan" los pagos una vez creados,
        # pero si lo necesitaras, la lógica iría aquí.
        # Por ejemplo, para modificar el 'reference' o 'concept' (aunque no el monto).
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# --- RentalSerializer Principal (Sin cambios relevantes para este problema, pero incluido por completitud) ---
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
            "vehicle_daily_price",
            "vehicle_make",
            "vehicle_model",
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
class RentalFinalizeSerializer(serializers.Serializer): # Cambiado a Serializer en lugar de ModelSerializer
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

        el_salvador_tz = pytz.timezone('America/El_Salvador')

        if rental.status == 'Finalizado':
            raise serializers.ValidationError({"status": "Este alquiler ya ha sido finalizado."})
        if rental.status == 'Cancelado':
            raise serializers.ValidationError({"status": "Este alquiler ha sido cancelado y no puede ser finalizado."})
        if rental.status == 'Pendiente':
            raise serializers.ValidationError({"status": "Este alquiler está Pendiente. No se puede finalizar hasta que esté Activo o Reservado."})

        actual_return_date_local = actual_return_date.astimezone(el_salvador_tz)
        rental_start_date_local_tz = rental.start_date.astimezone(el_salvador_tz)
        
        if actual_return_date_local < rental_start_date_local_tz:
            raise serializers.ValidationError({"actual_return_date": "La fecha de devolución real no puede ser anterior a la fecha de inicio del alquiler."})
        
        current_time_in_local_tz = timezone.now().astimezone(el_salvador_tz)
        if actual_return_date_local > current_time_in_local_tz + timedelta(minutes=1):
            raise serializers.ValidationError({"actual_return_date": "La fecha de devolución real no puede ser una fecha futura."})

        fuel_level_map = {choice[0]: i for i, choice in enumerate(Rental.FUEL_LEVEL_CHOICES)}
        pickup_level = fuel_level_map.get(rental.fuel_level_pickup, 0)
        return_level = fuel_level_map.get(fuel_level_return, 0)

        fuel_charge = decimal.Decimal('0.00')
        FUEL_COST_PER_LEVEL = decimal.Decimal('15.00')

        if return_level < pickup_level:
            fuel_charge = (pickup_level - return_level) * FUEL_COST_PER_LEVEL
        
        data['calculated_fuel_charge'] = fuel_charge.quantize(decimal.Decimal('0.01'))

        overdue_charge = decimal.Decimal('0.00')
        days_overdue = 0

        rental_end_date_local_tz = rental.end_date.astimezone(el_salvador_tz)
        
        if actual_return_date_local > rental_end_date_local_tz:
            
            diff_time = actual_return_date_local - rental_end_date_local_tz

            diff_hours = diff_time.total_seconds() / (60 * 60)
            raw_days_overdue = math.ceil(diff_hours / 24)

            if raw_days_overdue <= 0 and diff_hours > 0:
                raw_days_overdue = 1

            days_overdue = raw_days_overdue

            daily_price = rental.vehicle.daily_price

            if days_overdue <= 3:
                overdue_charge = daily_price * days_overdue
            elif days_overdue > 3 and days_overdue <= 7:
                overdue_acu = daily_price * 3
                overdue_charge = overdue_acu + (daily_price * (days_overdue - 3) * 2)
            else: # Más de 7 días
                overdue_acu = daily_price * 3
                overdue_charge = overdue_acu + (daily_price * (7 - 3) * 2)
        
        data['calculated_overdue_charge'] = overdue_charge.quantize(decimal.Decimal('0.01'))
        data['days_overdue'] = days_overdue

        total_original_rental_cost = rental.total_price 
        if not isinstance(total_original_rental_cost, decimal.Decimal):
            total_original_rental_cost = decimal.Decimal(str(total_original_rental_cost)).quantize(decimal.Decimal('0.01'))

        # Total que se debe cubrir por el alquiler, cargos por atraso y combustible
        total_amount_to_cover = (total_original_rental_cost + overdue_charge + fuel_charge).quantize(decimal.Decimal('0.01'))
        
        # Pagos existentes por conceptos de servicio (anticipo, pago final, cargos adicionales)
        # Excluye depósitos y reembolsos de este cálculo inicial
        paid_for_rental_only = Payment.objects.filter(
            rental=rental,
            concept__in=['Anticipo', 'Pago Final', 'Cargo Adicional', 'Cargo por Retraso'] 
        ).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')

        # Depósito de garantía real recibido (monto que existe en BD, será 0 para nacionales si no lo pagaron)
        deposit_received_amount = decimal.Decimal('0.00')
        deposit_payment = Payment.objects.filter(rental=rental, concept='Depósito').first()
        if deposit_payment:
            deposit_received_amount = deposit_payment.amount

        # Monto del pago que viene en la solicitud actual (si aplica)
        current_payment_in_request_amount = decimal.Decimal('0.00')
        payment_concept = None
        if final_payment_data and final_payment_data.get('amount') is not None:
            current_payment_in_request_amount = decimal.Decimal(str(final_payment_data.get('amount'))).quantize(decimal.Decimal('0.01'))
            payment_concept = final_payment_data.get('concept')
        
        # Determine si el cliente es extranjero
        is_foreign_customer = False
        if hasattr(rental.customer, 'customer_type') and rental.customer.customer_type and rental.customer.customer_type.lower() == 'extranjero':
            is_foreign_customer = True

        DEPOSIT_AMOUNT_FOREIGNER = decimal.Decimal('100.00') # El valor fijo para depósitos de extranjeros

        # --- CÁLCULO INICIAL DEL SALDO PENDIENTE (ANTES DE APLICAR EL PAGO ACTUAL O DEPÓSITO) ---
        # Este es el monto que realmente se debe por el servicio, sin incluir aún el pago que viene en el request
        # ni el crédito del depósito de extranjero.
        balance_owed_for_service_before_current_payment = (total_amount_to_cover - paid_for_rental_only).quantize(decimal.Decimal('0.01'))
        
        total_calculated_refund_amount = decimal.Decimal('0.00') # Inicializar para todos los flujos

        # --- VALIDACIÓN DEL PAGO FINAL / CÁLCULO DE REEMBOLSO ---
        if final_payment_data:
            # Si el pago que viene es un reembolso, validamos contra el monto calculable
            if payment_concept == 'Reembolso':
                # Calcular el monto total disponible para reembolso.
                # Considerar el balance del servicio y el depósito.
                # Si el servicio ya está pagado (balance_owed_for_service_before_current_payment <= 0)
                # y el cliente es extranjero, los $100 se reembolsan.
                # Si el servicio ya está pagado (balance_owed_for_service_before_current_payment <= 0)
                # y el cliente es nacional, se reembolsa su depósito (que puede ser 0).
                
                # Primero, el reembolso potencial por sobrepago de servicio existente
                if balance_owed_for_service_before_current_payment < decimal.Decimal('0.00'):
                    total_calculated_refund_amount += abs(balance_owed_for_service_before_current_payment)
                
                # Luego, el reembolso del depósito si el servicio está cubierto
                # Esto es: si no hay deuda de servicio O si la deuda existente puede ser cubierta por el depósito de extranjero
                # Para extranjeros, el depósito SIEMPRE se reembolsa si el servicio está cubierto.
                # Para nacionales, se reembolsa el deposit_received_amount si el servicio está cubierto.
                effective_balance_after_deposit_credit = balance_owed_for_service_before_current_payment

                if is_foreign_customer:
                    effective_balance_after_deposit_credit = balance_owed_for_service_before_current_payment - DEPOSIT_AMOUNT_FOREIGNER
                
                if effective_balance_after_deposit_credit < decimal.Decimal('0.00'):
                    # Si después de aplicar el depósito (para extranjero) o si el servicio ya estaba sobrepagado,
                    # hay un saldo negativo, ese es un monto a reembolsar.
                    total_calculated_refund_amount += abs(effective_balance_after_deposit_credit)
                
                # Para Nacionales, si el servicio está cubierto (balance_owed_for_service_before_current_payment <= 0)
                # y tienen un depósito (deposit_received_amount > 0), se les reembolsa.
                # NOTA: Aquí separamos para no sumar el depósito si ya se manejó en effective_balance_after_deposit_credit
                # (que sería el caso para extranjeros que usaron el depósito para cubrir deuda).
                if not is_foreign_customer and balance_owed_for_service_before_current_payment <= decimal.Decimal('0.00') and deposit_received_amount > decimal.Decimal('0.00'):
                    total_calculated_refund_amount += deposit_received_amount


                if total_calculated_refund_amount <= decimal.Decimal('0.00'):
                     raise serializers.ValidationError({"final_payment": "No hay monto pendiente para reembolsar."})
                
                if current_payment_in_request_amount > total_calculated_refund_amount: 
                    raise serializers.ValidationError(
                        {"final_payment": f"El monto del reembolso excede el total a reembolsar. Monto máximo a reembolsar: ${total_calculated_refund_amount:.2f}."}
                    )
                # Convertir el monto a negativo para almacenarlo en la base de datos como un reembolso
                data['final_payment']['amount'] = -current_payment_in_request_amount
                
                # Una vez que se procesa un reembolso explícito, el saldo pendiente queda en 0
                remaining_balance_for_service = decimal.Decimal('0.00')

            # Si el pago es un monto POSITIVO (un pago normal, no un reembolso)
            else: 
                # Saldo que el cliente aún debe por el servicio (sin considerar el pago actual del request)
                debt_after_existing_payments = balance_owed_for_service_before_current_payment

                if debt_after_existing_payments > decimal.Decimal('0.00'): # Si aún hay deuda de servicio
                    amount_to_check_against_debt = current_payment_in_request_amount
                    if is_foreign_customer:
                        amount_to_check_against_debt += DEPOSIT_AMOUNT_FOREIGNER # El depósito de $100 se usa como crédito
                    
                    if amount_to_check_against_debt < debt_after_existing_payments:
                        amount_missing = debt_after_existing_payments - amount_to_check_against_debt
                        error_message = f"El monto del pago es insuficiente. Quedan ${amount_missing:.2f} pendientes por el servicio de alquiler y cargos."
                        if is_foreign_customer:
                            error_message += " (Considerando el uso de su depósito de $100)."
                        raise serializers.ValidationError({"final_payment": error_message + " Por favor, ajuste el pago final."})
                    
                    # Si el pago actual + (depósito extranjero si aplica) cubre o sobrepasa la deuda
                    if amount_to_check_against_debt >= debt_after_existing_payments:
                        overpayment_from_service_and_deposit = amount_to_check_against_debt - debt_after_existing_payments
                        total_calculated_refund_amount = overpayment_from_service_and_deposit
                        remaining_balance_for_service = decimal.Decimal('0.00') # La deuda de servicio queda en 0
                else: # Si el servicio ya estaba cubierto o sobrepagado ANTES del pago actual
                    # Si el servicio ya está cubierto, cualquier pago adicional es un sobrepago a reembolsar
                    total_calculated_refund_amount += abs(debt_after_existing_payments) # Cualquier sobrepago existente
                    total_calculated_refund_amount += current_payment_in_request_amount # El pago actual
                    
                    # Además, si el servicio ya estaba cubierto, y es extranjero, se reembolsa el depósito fijo
                    if is_foreign_customer and deposit_received_amount == DEPOSIT_AMOUNT_FOREIGNER:
                        total_calculated_refund_amount += DEPOSIT_AMOUNT_FOREIGNER
                    # Si es nacional y el servicio ya está cubierto, y tiene depósito, se reembolsa
                    elif not is_foreign_customer and deposit_received_amount > decimal.Decimal('0.00'):
                        total_calculated_refund_amount += deposit_received_amount

                    remaining_balance_for_service = decimal.Decimal('0.00')

        # --- Si NO se envió un pago final (final_payment_data is None) ---
        else:
            # Calcular el reembolso potencial si no hay un pago final, para validación
            effective_balance_at_finalization = balance_owed_for_service_before_current_payment # Deuda sin el pago actual

            if is_foreign_customer:
                effective_balance_at_finalization -= DEPOSIT_AMOUNT_FOREIGNER # Restamos el crédito de $100

            if effective_balance_at_finalization < decimal.Decimal('0.00'):
                total_calculated_refund_amount += abs(effective_balance_at_finalization)
            
            # Para nacionales, si el servicio está cubierto, el depósito real es reembolso
            if not is_foreign_customer and balance_owed_for_service_before_current_payment <= decimal.Decimal('0.00') and deposit_received_amount > decimal.Decimal('0.00'):
                total_calculated_refund_amount += deposit_received_amount


            if balance_owed_for_service_before_current_payment > decimal.Decimal('0.00') and effective_balance_at_finalization > decimal.Decimal('0.00'):
                # Si el saldo de servicio (sin depósito) es positivo Y aún lo es con el crédito de depósito
                raise serializers.ValidationError(
                    {"final_payment": f"No se proporcionó un pago final, y aún quedan ${effective_balance_at_finalization:.2f} pendientes por el servicio de alquiler y cargos."}
                )
            elif total_calculated_refund_amount > decimal.Decimal('0.00'):
                raise serializers.ValidationError(
                    {"final_payment": f"Existe un monto de ${total_calculated_refund_amount:.2f} a reembolsar, pero no se proporcionó información de pago final."}
                )
            
            # Si no hay pago final y no hay deuda, ni reembolso pendiente, el saldo final es 0
            remaining_balance_for_service = decimal.Decimal('0.00')


        # Si el proceso llega aquí, las validaciones pasaron
        # Se almacenan las variables calculadas en `data` para el método `save`
        data['total_amount_to_cover'] = total_amount_to_cover
        data['total_paid_for_service_excluding_current_payment'] = paid_for_rental_only # Solo pagos anteriores
        data['remaining_balance_for_service_final'] = remaining_balance_for_service # Saldo final, debe ser 0 si se cubrió
        data['deposit_received_amount'] = deposit_received_amount 
        data['total_calculated_refund_amount'] = total_calculated_refund_amount.quantize(decimal.Decimal('0.01'))
        data['is_foreign_customer'] = is_foreign_customer # Guardar para save method


        return data

    @transaction.atomic
    def save(self, **kwargs):
        rental = self.instance
        actual_return_date = self.validated_data['actual_return_date']
        fuel_level_return = self.validated_data['fuel_level_return']
        remarks = self.validated_data.get('remarks')
        final_payment_data = self.validated_data.get('final_payment')

        # Estos valores ya vienen calculados del método validate
        total_amount_to_cover = self.validated_data['total_amount_to_cover']
        total_calculated_refund_amount = self.validated_data['total_calculated_refund_amount'] 
        remaining_balance_for_service_final = self.validated_data['remaining_balance_for_service_final'] # Este es el saldo final, que debe ser 0
        deposit_received_amount = self.validated_data['deposit_received_amount']
        is_foreign_customer = self.validated_data['is_foreign_customer'] # Usar en save method


        user_id = kwargs.get('modified_by', None)
        if user_id:
            rental.modified_by = user_id

        rental.actual_return_date = actual_return_date
        rental.fuel_level_return = fuel_level_return
        rental.remarks = remarks
        
        # total_price de la renta ahora reflejará el costo total original + cargos por atraso y combustible
        rental.total_price = total_amount_to_cover

        base_payment_type = final_payment_data.get('payment_type', 'Efectivo') if final_payment_data else 'Efectivo'

        # 1. Registrar el pago final si se envió y es un monto positivo (no un reembolso)
        if final_payment_data and final_payment_data.get('amount', 0) > 0:
            # Verifica si ya se hizo un pago con el mismo monto y concepto para evitar duplicados.
            if not Payment.objects.filter(
                rental=rental,
                concept=final_payment_data['concept'], 
                amount=final_payment_data['amount'],
                payment_type=final_payment_data.get('payment_type', 'Efectivo')
            ).exists():
                Payment.objects.create(
                    rental=rental,
                    amount=final_payment_data['amount'],
                    payment_type=final_payment_data.get('payment_type', 'Efectivo'),
                    concept=final_payment_data.get('concept', 'Pago Final'), 
                    reference=final_payment_data.get('reference', f"Pago final Renta #{rental.id}"),
                    payment_date=timezone.now(),
                    created_by=user_id,
                    modified_by=user_id
                )

        # 2. Manejo del reembolso (si el `total_calculated_refund_amount` es mayor a 0)
        # Esto creará el Payment del reembolso automáticamente si no se pasó ya como final_payment
        if total_calculated_refund_amount > decimal.Decimal('0.00'):
            # Si el final_payment_data es un reembolso y el monto coincide, ya se creó, no duplicar
            is_refund_payment_already_in_request = (
                final_payment_data and 
                final_payment_data['concept'] == 'Reembolso' and 
                abs(final_payment_data['amount']) == total_calculated_refund_amount
            )

            if not is_refund_payment_already_in_request:
                refund_concept = 'Reembolso' 
                refund_reference_detail = ""
                
                # Determinar el detalle específico para el campo 'reference'
                # La lógica aquí es más compleja para determinar el origen del reembolso.
                # Podría ser:
                # - El servicio fue sobrepagado (e.g., balance_owed_for_service_before_current_payment < 0)
                # - El depósito extranjero se usó para cubrir y sobró.
                # - El depósito nacional se devuelve.

                # Una manera más robusta de determinar el origen sería guardarlo en `validate`
                # Por ahora, una aproximación:
                if is_foreign_customer and deposit_received_amount == decimal.Decimal('100.00') and total_calculated_refund_amount >= decimal.Decimal('100.00'):
                    refund_reference_detail = 'Depósito Extranjero y/o Sobrepago'
                elif deposit_received_amount > decimal.Decimal('0.00') and total_calculated_refund_amount >= deposit_received_amount:
                     refund_reference_detail = 'Depósito Nacional y/o Sobrepago'
                else:
                    refund_reference_detail = 'Sobrepago del servicio' # Por defecto si no encaja en las anteriores
                
                refund_reference = f"Reembolso de {refund_reference_detail} Renta #{rental.id}"


                # Verifica si ya se hizo un reembolso con el mismo monto y concepto para evitar duplicados.
                # Se busca por el valor absoluto del monto, ya que en la BD se guarda como negativo.
                if not Payment.objects.filter(
                    rental=rental,
                    concept=refund_concept, 
                    amount=total_calculated_refund_amount * -1 
                ).exists(): 
                    Payment.objects.create(
                        rental=rental,
                        amount=total_calculated_refund_amount * -1, # Monto negativo para indicar reembolso
                        payment_type=base_payment_type, # Puede que quieras un tipo de pago específico para reembolsos
                        payment_date=timezone.now(),
                        concept=refund_concept, 
                        reference=refund_reference, 
                        created_by=user_id,
                        modified_by=user_id
                    )

        # 3. Actualizar el estado de la renta a 'Finalizado'
        rental.status = 'Finalizado'

        # 4. Actualizar el estado del vehículo
        rental.vehicle.status = 'Disponible' 
        rental.vehicle.save()

        rental.save()
        
        return rental
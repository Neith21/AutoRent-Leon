# payment/serializers.py
from rest_framework import serializers
from payment.models import Payment
from rental.models import Rental 
from django.utils import timezone
import decimal
from django.db.models import Sum 
from django.contrib.auth.models import User # Necesitamos importar User para created_by_name y modified_by_name

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Payment.
    """
    # rental = serializers.PrimaryKeyRelatedField(queryset=Rental.objects.all()) # Esta línea ya no es necesaria si usas extra_kwargs

    # Campos para mostrar el nombre del usuario
    created_by_name = serializers.SerializerMethodField(read_only=True)
    modified_by_name = serializers.SerializerMethodField(read_only=True)

    # Formateo de fechas para asegurar la salida consistente
    payment_date = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M",
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        default_timezone=timezone.get_current_timezone(),
        read_only=True # Lo hacemos read_only aquí porque se asigna automáticamente en create
    )
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'rental',
            'amount',
            'payment_type',
            'payment_date',
            'concept',
            'reference',
            'active',
            'created_by',
            'created_by_name', # Incluir el nombre del creador
            'created_at',
            'modified_by',
            'modified_by_name', # Incluir el nombre del modificador
            'updated_at',
        ]
        # --- ¡CAMBIO CLAVE AQUÍ! ---
        # Hacemos que 'rental' no sea requerido cuando se usa en un contexto de creación anidada
        # (ya que el RentalSerializer lo asigna después), pero permitimos que se envíe si es necesario.
        extra_kwargs = {
            'rental': {'required': False, 'allow_null': True}
        }
        # Ya no necesitamos read_only_fields de esta forma tan explícita,
        # ya que los definimos directamente como read_only en el campo o via extra_kwargs si aplica.
        # Pero los dejaremos para no romper algo si tienes lógica específica con ellos.
        read_only_fields = ['id', 'payment_date', 'created_at', 'updated_at', 'created_by', 'modified_by'] 

    # Método para obtener el nombre del usuario que creó el pago
    def get_created_by_name(self, obj):
        if obj.created_by is None:
            return None
        try:
            user = User.objects.get(id=obj.created_by)
            return user.first_name if user.first_name else user.username # O el campo que uses para el nombre
        except (User.DoesNotExist, ValueError):
            return None

    # Método para obtener el nombre del usuario que modificó el pago
    def get_modified_by_name(self, obj):
        if obj.modified_by is None:
            return None
        try:
            user = User.objects.get(id=obj.modified_by)
            return user.first_name if user.first_name else user.username # O el campo que uses para el nombre
        except (User.DoesNotExist, ValueError):
            return None

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user.id
        
        # payment_date se asigna automáticamente a timezone.now() si no viene en el payload
        if 'payment_date' not in validated_data:
            validated_data['payment_date'] = timezone.now()

        return Payment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['modified_by'] = request.user.id
        
        # Eliminar 'payment_date' de validated_data si no es writable para evitar errores.
        # Ya lo marcamos como read_only en el campo de arriba.
        validated_data.pop('payment_date', None) 

        return super().update(instance, validated_data)

    def validate(self, data):
        """
        Validaciones personalizadas para el pago:
        - El alquiler debe existir y estar activo.
        - Reglas de negocio para anticipos y depósitos.
        """
        # Si 'rental' no se envía, y este serializer se usa en un contexto no anidado,
        # o si la instancia de la renta no está disponible en el contexto (como en create_with_initial_payment),
        # entonces 'rental' puede ser None.
        rental_instance = data.get('rental', None)
        
        # Si estamos creando un pago anidado, la instancia de renta aún no existe aquí,
        # pero estará disponible en el método 'create' del RentalSerializer padre.
        # Por lo tanto, si rental_instance es None, solo continuamos si estamos en un contexto de create
        # donde la renta se asignará después.
        
        # Esta validación es importante para pagos no anidados o actualizaciones.
        # Para el caso de create_with_initial_payment, 'rental' NO viene en el payload del Payment,
        # así que la validación a nivel de objeto 'rental' debe ser manejada en el RentalSerializer.
        # Aquí, si rental_instance es None, no podemos hacer validaciones sobre el rental aún.

        # Solo valida si 'rental' está presente (ya sea porque se envió o ya está en la instancia).
        if rental_instance:
            if not Rental.objects.filter(id=rental_instance.id, active=True).exists():
                raise serializers.ValidationError({"rental": "El alquiler especificado no existe o no está activo."})

            rental = rental_instance

            amount = data.get('amount')
            concept = data.get('concept')

            # --- Lógica de Validación para Anticipo y Depósito ---
            if concept == 'Anticipo':
                if not rental.total_price:
                    raise serializers.ValidationError({"rental": "El alquiler no tiene un precio total definido."})

                total_rental_price = rental.total_price
                
                duration_total_seconds = (rental.end_date - rental.start_date).total_seconds()
                duration_days = int(duration_total_seconds / (24 * 3600))
                if duration_total_seconds % (24 * 3600) > 0 or duration_days == 0:
                    duration_days += 1

                required_initial_payment_percentage = decimal.Decimal('0.50')
                if duration_days > 5:
                    required_initial_payment_percentage = decimal.Decimal('1.00')

                expected_anticipo = total_rental_price * required_initial_payment_percentage
                
                paid_anticipo_so_far = Payment.objects.filter(
                    rental=rental,
                    concept='Anticipo',
                    active=True
                ).exclude(id=self.instance.id if self.instance else None).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')

                remaining_anticipo = expected_anticipo - paid_anticipo_so_far

                if amount > remaining_anticipo + decimal.Decimal('0.01'):
                    raise serializers.ValidationError(
                        {"amount": f"El monto del anticipo (${amount:.2f}) excede el monto restante requerido (${remaining_anticipo:.2f})."}
                    )
            
            if rental.customer.customer_type == 'extranjero' and concept == 'Deposito':
                expected_deposit = decimal.Decimal('100.00')
                paid_deposit_so_far = Payment.objects.filter(
                    rental=rental,
                    concept='Deposito', 
                    active=True
                ).exclude(id=self.instance.id if self.instance else None).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')
                
                remaining_deposit = expected_deposit - paid_deposit_so_far

                if amount > remaining_deposit + decimal.Decimal('0.01'):
                    raise serializers.ValidationError(
                        {"amount": f"El monto del depósito (${amount:.2f}) excede lo requerido (${remaining_deposit:.2f})."}
                    )
                elif amount < expected_deposit and remaining_deposit > 0:
                    pass 

            elif rental.customer.customer_type != 'extranjero' and concept == 'Deposito':
                raise serializers.ValidationError({"concept": "No se requiere depósito para clientes nacionales."})

        return data
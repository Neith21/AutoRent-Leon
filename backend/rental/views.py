# rental/views.py

from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus
import decimal
from django.db import transaction
from rest_framework import serializers

# Importa tus modelos
from rental.models import Rental
from customer.models import Customer
from vehicle.models import Vehicle
from payment.models import Payment

# Importa tus serializadores
from rental.serializers import RentalSerializer, RentalFinalizeSerializer
from payment.serializers import PaymentSerializer

# Importa tus decoradores y permisos personalizados
from utilities.decorators import authenticate_user

# Otras importaciones necesarias para tus validaciones y cálculos
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

# --- SERIALIZADOR PARA CALCULAR PRECIO (sin cambios relevantes) ---
class RentalCalculatePriceInputSerializer(serializers.Serializer):
    customer = serializers.IntegerField(required=True)
    vehicle = serializers.IntegerField(required=True)
    start_date = serializers.DateTimeField(
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        default_timezone=timezone.get_current_timezone()
    )
    end_date = serializers.DateTimeField(
        input_formats=['%d-%m-%Y %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        default_timezone=timezone.get_current_timezone()
    )


# --- Vistas de Alquiler ---

class RentalRC(APIView):
    """
    Vista de API para listar (R, read) y crear (C, create) Alquileres.
    Esta vista maneja la creación de rentas SIN pagos iniciales (solo reserva).
    """
    @authenticate_user(required_permission='rental.view_rental')
    def get(self, request):
        try:
            # === CORRECCIÓN APLICADA AQUÍ: prefetch_related('payment_set') es CORRECTO ===
            # Dado que el ForeignKey en Payment se llama 'rental', el related_name por defecto es 'payment_set'.
            data = Rental.objects.filter(active=True).select_related(
                'customer',
                'vehicle',
                'pickup_branch',
                'return_branch'
            ).prefetch_related(
                'payment_set' # Nombre correcto del RelatedManager para Payment en Rental
            ).order_by('-start_date')

            serializer = RentalSerializer(data, many=True)
            return JsonResponse({
                "data": serializer.data
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    @authenticate_user(required_permission='rental.add_rental')
    def post(self, request):
        """
        Maneja las solicitudes POST para crear un nuevo alquiler en estado 'Reservado' (por defecto).
        Este endpoint NO espera ni procesa pagos iniciales anidados.
        """
        with transaction.atomic():
            data = request.data.copy()
            if 'status' not in data:
                data['status'] = 'Reservado'

            serializer = RentalSerializer(data=data, context={'request': request})
            try:
                serializer.is_valid(raise_exception=True)

                user_id = request.user.id if request.user.is_authenticated else None

                rental = serializer.save(created_by=user_id)

                response_data = {
                    "id": rental.id,
                    "message": "Renta creada en estado 'Reservado'.",
                    "rental_details": RentalSerializer(rental).data
                }
                return JsonResponse(response_data, status=HTTPStatus.CREATED)

            except Exception as e:
                if hasattr(e, 'detail'):
                    return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
                return JsonResponse(
                    {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

# --- VISTA PARA CREAR RENTA CON PAGO INICIAL ATÓMICAMENTE ---
class RentalCreateWithInitialPaymentAPIView(APIView):
    """
    Vista de API para crear un nuevo Alquiler con un pago inicial
    dentro de una transacción atómica.
    """
    @authenticate_user(required_permission='rental.add_rental')
    def post(self, request):
        with transaction.atomic():
            data = request.data.copy()
            if 'status' not in data:
                data['status'] = 'Activo'

            serializer = RentalSerializer(data=data, context={'request': request})
            try:
                serializer.is_valid(raise_exception=True)

                user_id = request.user.id if request.user.is_authenticated else None

                rental = serializer.save(created_by=user_id)

                response_data = {
                    "id": rental.id,
                    "message": "Renta y pago(s) inicial(es) registrados exitosamente.",
                    "rental_details": RentalSerializer(rental).data
                }
                return JsonResponse(response_data, status=HTTPStatus.CREATED)

            except Exception as e:
                if hasattr(e, 'detail'):
                    return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
                return JsonResponse(
                    {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

# --- RESTO DE VISTAS ---

class RentalRetrieveUpdateDestroy(APIView):
    @authenticate_user(required_permission='rental.view_rental')
    def get(self, request, pk):
        try:
            # === CORRECCIÓN APLICADA AQUÍ: prefetch_related('payment_set') es CORRECTO ===
            # Dado que el ForeignKey en Payment se llama 'rental', el related_name por defecto es 'payment_set'.
            rental = Rental.objects.prefetch_related('payment_set').get(pk=pk, active=True)
            serializer = RentalSerializer(rental)
            return JsonResponse(serializer.data, status=HTTPStatus.OK)
        except Rental.DoesNotExist:
            return JsonResponse({"detail": "Renta no encontrada o inactiva."}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    @authenticate_user(required_permission='rental.change_rental')
    def put(self, request, pk):
        with transaction.atomic():
            try:
                rental = Rental.objects.get(pk=pk, active=True)
                serializer = RentalSerializer(rental, data=request.data, partial=True, context={'request': request})
                serializer.is_valid(raise_exception=True)

                user_id = request.user.id if request.user.is_authenticated else None
                rental_updated = serializer.save(modified_by=user_id)

                return JsonResponse(RentalSerializer(rental_updated).data, status=HTTPStatus.OK)
            except Rental.DoesNotExist:
                return JsonResponse({"detail": "Renta no encontrada o inactiva."}, status=HTTPStatus.NOT_FOUND)
            except Exception as e:
                if hasattr(e, 'detail'):
                    return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
                return JsonResponse(
                    {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

    @authenticate_user(required_permission='rental.delete_rental')
    def delete(self, request, pk):
        with transaction.atomic():
            try:
                rental = Rental.objects.get(pk=pk, active=True)

                # Lógica para manejar el estado del vehículo al eliminar una renta
                if rental.status in ['Activo', 'Reservado']:
                    vehicle = rental.vehicle
                    vehicle.status = 'Disponible'  # Asumimos que se libera el vehículo
                    vehicle.save()

                rental.active = False
                user_id = request.user.id if request.user.is_authenticated else None
                rental.modified_by = user_id
                rental.save()

                return JsonResponse({"message": "Renta desactivada exitosamente."}, status=HTTPStatus.NO_CONTENT)
            except Rental.DoesNotExist:
                return JsonResponse({"detail": "Renta no encontrada o inactiva."}, status=HTTPStatus.NOT_FOUND)
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

class RentalFinalizeAPIView(APIView):
    @authenticate_user(required_permission='rental.change_rental')
    def post(self, request, pk):
        try:
            rental = Rental.objects.get(pk=pk, active=True)
        except Rental.DoesNotExist:
            return JsonResponse({"detail": "Renta no encontrada o inactiva."}, status=HTTPStatus.NOT_FOUnd)

        serializer = RentalFinalizeSerializer(data=request.data, context={'rental': rental})
        try:
            serializer.is_valid(raise_exception=True)
            user_id = request.user.id if request.user.is_authenticated else None
            finalized_rental = serializer.save(modified_by=user_id)
            return JsonResponse(RentalSerializer(finalized_rental).data, status=HTTPStatus.OK)
        except Exception as e:
            if hasattr(e, 'detail'):
                return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al finalizar la renta: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

class RentalAddPaymentAPIView(APIView):
    """
    Endpoint para agregar pagos a una renta existente.
    """
    @authenticate_user(required_permission='payment.add_payment')
    def post(self, request, pk):
        try:
            rental = Rental.objects.get(pk=pk, active=True)
        except Rental.DoesNotExist:
            return JsonResponse({"detail": "Renta no encontrada o inactiva."}, status=HTTPStatus.NOT_FOUND)

        serializer = PaymentSerializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user_id = request.user.id if request.user.is_authenticated else None
            payment = serializer.save(rental=rental, created_by=user_id)
            return JsonResponse(PaymentSerializer(payment).data, status=HTTPStatus.CREATED)
        except Exception as e:
            if hasattr(e, 'detail'):
                return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar el pago: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_SERVER_ERROR
            )

class RentalCalculatePriceAPIView(APIView):
    """
    Endpoint para precálculo de precio, pago inicial requerido,
    y validaciones de límites de vehículos sin crear el alquiler.
    """
    @authenticate_user(required_permission='rental.view_rental')
    def post(self, request):
        serializer = RentalCalculatePriceInputSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            if hasattr(e, 'detail'):
                return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
            return JsonResponse(
                {"detail": f"Error en la validación de entrada: {str(e)}"},
                status=HTTPStatus.BAD_REQUEST
            )

        customer_id = serializer.validated_data['customer']
        vehicle_id = serializer.validated_data['vehicle']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        try:
            customer = Customer.objects.get(id=customer_id)
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except (Customer.DoesNotExist, Vehicle.DoesNotExist):
            return JsonResponse({"detail": "ID de cliente/vehículo inválido."}, status=HTTPStatus.BAD_REQUEST)

        errors = []
        response_data = {}

        if customer.status == 'lista_negra':
            errors.append("El cliente está en la lista negra y no puede alquilar vehículos.")
        if not customer.active:
            errors.append("El cliente no está activo.")

        if start_date < timezone.now() - timedelta(minutes=1):
            errors.append("La fecha de inicio no puede ser en el pasado.")
        if end_date <= start_date:
            errors.append("La fecha de fin debe ser posterior a la fecha de inicio.")

        if not vehicle.active:
            errors.append("El vehículo no está activo.")

        conflicting_rentals = Rental.objects.filter(
            vehicle=vehicle,
            end_date__gt=start_date,
            start_date__lt=end_date,
            status__in=['Activo', 'Reservado'],
            active=True
        ).exists()

        if conflicting_rentals:
            errors.append("El vehículo no está disponible para las fechas seleccionadas debido a un alquiler existente.")

        if vehicle.status != 'Disponible':
            errors.append(f"El vehículo está actualmente marcado como no disponible en su estado general: {vehicle.status}.")

        active_rentals_count = Rental.objects.filter(
            customer=customer,
            status__in=['Activo', 'Reservado'],
            active=True
        ).count()

        if customer.customer_type == 'nacional' and active_rentals_count >= 5:
            errors.append(f"Cliente nacional ya ha alcanzado el límite de {active_rentals_count} de 5 vehículos simultáneos.")
        elif customer.customer_type == 'extranjero' and active_rentals_count >= 3:
            errors.append(f"Cliente extranjero ya ha alcanzado el límite de {active_rentals_count} de 3 vehículos simultáneos.")

        if not errors:
            if vehicle.daily_price is None or vehicle.daily_price <= 0:
                errors.append("El precio diario del vehículo es inválido o no está configurado.")

            customer_type_normalized = customer.customer_type.lower() if customer.customer_type else ''

            if customer_type_normalized not in ['nacional', 'extranjero']:
                errors.append("El tipo de cliente es desconocido.")

            if not errors:
                try:
                    duration = end_date - start_date

                    duration_days = duration.days

                    if duration.seconds > 0 or (duration.days == 0 and duration.total_seconds() > 0):
                        duration_days += 1

                    if duration_days == 0 and duration.total_seconds() > 0:
                        duration_days = 1

                    if duration_days <= 0:
                        errors.append("La duración del alquiler debe ser al menos un día.")
                    else:
                        daily_price = decimal.Decimal(str(vehicle.daily_price))
                        total_price = daily_price * decimal.Decimal(str(duration_days))
                        response_data['total_price'] = total_price.quantize(decimal.Decimal('0.01'))

                        required_initial_payment_percentage = decimal.Decimal('0.50')
                        if duration_days > 5:
                            required_initial_payment_percentage = decimal.Decimal('1.00')

                        required_initial_rental_payment = total_price * required_initial_payment_percentage
                        response_data['required_initial_rental_payment'] = required_initial_rental_payment.quantize(decimal.Decimal('0.01'))

                        deposit_required = decimal.Decimal('0.00')
                        if customer_type_normalized == 'extranjero':
                            deposit_required = decimal.Decimal('100.00')
                        response_data['deposit_required'] = deposit_required.quantize(decimal.Decimal('0.01'))

                        response_data['total_amount_due_at_start'] = (required_initial_rental_payment + deposit_required).quantize(decimal.Decimal('0.01'))

                except Exception as calc_error:
                    errors.append(f"Error durante el cálculo del precio: {str(calc_error)}")

        if errors:
            return JsonResponse({"detail": errors}, status=HTTPStatus.BAD_REQUEST)
        else:
            return JsonResponse(response_data, status=HTTPStatus.OK)
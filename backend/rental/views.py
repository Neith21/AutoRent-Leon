from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus # Para los códigos de estado HTTP
import decimal

# Importa tus modelos
from rental.models import Rental
from customer.models import Customer # Necesario para RentalCalculatePriceAPIView
from vehicle.models import Vehicle   # Necesario para RentalCalculatePriceAPIView
from invoice.models import Invoice   # Si lo vas a usar, manténlo
from payment.models import Payment   # Si lo vas a usar, manténlo

# Importa tus serializadores
from rental.serializers import RentalSerializer, RentalFinalizeSerializer # <--- ¡AQUÍ ESTÁ LA CORRECCIÓN CLAVE!
from payment.serializers import PaymentSerializer # <--- ¡TAMBIÉN ES NECESARIO SI USAS RentalAddPaymentAPIView!

# Importa tus decoradores y permisos personalizados
from utilities.decorators import authenticate_user

# Si no tienes la app 'core' y no la quieres crear, DEBERÁS ASEGURARTE
# de que `authenticate_user` no dependa de `HasAppPermission`
# Si `authenticate_user` usa internamente `request.user.has_perm`,
# entonces NO NECESITAS importar `HasAppPermission` aquí.
# Si lo necesitas, tendrías que crear la app `core` y el archivo `permissions.py`
# from core.permissions import HasAppPermission # <--- COMENTADO / ELIMINADO si no tienes app 'core'


# Otras importaciones necesarias para tus validaciones y cálculos
from django.utils import timezone
from datetime import timedelta
import decimal


# --- Vistas de Alquiler ---

class RentalRC(APIView):
    """
    Vista de API para listar (R, read) y crear (C, create) Alquileres.
    """
    @authenticate_user(required_permission='rental.view_rental')
    def get(self, request):
        """
        Maneja las solicitudes GET para devolver una lista de todos los alquileres activos.
        """
        try:
            data = Rental.objects.filter(active=True).select_related(
                'customer',
                'vehicle',
                'pickup_branch',
                'return_branch'
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
        Maneja las solicitudes POST para crear un nuevo alquiler.
        """
        serializer = RentalSerializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user_id = request.user.id if request.user.is_authenticated else None
            rental = serializer.save(created_by=user_id, total_price=serializer.validated_data['total_price'])

            response_data = RentalSerializer(rental).data
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(response_data, status=HTTPStatus.CREATED)
        except Exception as e:
            if hasattr(e, 'detail'):
                # CAMBIADO: Usando JsonResponse y HTTPStatus
                return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

class RentalRetrieveUpdateDestroy(APIView):
    """
    Vista para operaciones de recuperación (R), actualización (U) y eliminación (D)
    de un solo alquiler por su ID.
    """
    @authenticate_user(required_permission='rental.view_rental')
    def get(self, request, pk):
        """
        Maneja las solicitudes GET para devolver los detalles de un alquiler específico.
        """
        try:
            rental = Rental.objects.select_related(
                'customer', 'vehicle', 'pickup_branch', 'return_branch'
            ).get(pk=pk, active=True)
            serializer = RentalSerializer(rental)
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(serializer.data, status=HTTPStatus.OK)
        except Rental.DoesNotExist:
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Alquiler no encontrado."}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    @authenticate_user(required_permission='rental.change_rental')
    def put(self, request, pk):
        """
        Maneja las solicitudes PUT para actualizar completamente un alquiler existente.
        """
        try:
            rental = Rental.objects.get(pk=pk, active=True)
        except Rental.DoesNotExist:
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Alquiler no encontrado."}, status=HTTPStatus.NOT_FOUND)

        serializer = RentalSerializer(rental, data=request.data, partial=False, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user_id = request.user.id if request.user.is_authenticated else None
            updated_rental = serializer.save(modified_by=user_id)
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(RentalSerializer(updated_rental).data, status=HTTPStatus.OK)
        except Exception as e:
            if hasattr(e, 'detail'):
                # CAMBIADO: Usando JsonResponse y HTTPStatus
                return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    @authenticate_user(required_permission='rental.delete_rental')
    def delete(self, request, pk):
        """
        Maneja las solicitudes DELETE para desactivar (soft delete) un alquiler.
        """
        try:
            rental = Rental.objects.get(pk=pk, active=True)
            rental.active = False
            rental.modified_by = request.user.id if request.user.is_authenticated else None
            rental.save()
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Alquiler desactivado correctamente."}, status=HTTPStatus.NO_CONTENT)
        except Rental.DoesNotExist:
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Alquiler no encontrado."}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

class RentalCalculatePriceAPIView(APIView):
    """
    Endpoint para precálculo de precio, pago inicial requerido,
    y validaciones de límites de vehículos sin crear el alquiler.
    """
    @authenticate_user(required_permission='rental.view_rental') # O un permiso más general para cálculos
    def post(self, request):
        customer_id = request.data.get('customer')
        vehicle_id = request.data.get('vehicle')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')

        if not all([customer_id, vehicle_id, start_date_str, end_date_str]):
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Faltan campos obligatorios (customer, vehicle, start_date, end_date)."}, status=HTTPStatus.BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
            vehicle = Vehicle.objects.get(id=vehicle_id)
            start_date = timezone.datetime.strptime(start_date_str, "%d-%m-%Y %H:%M")
            end_date = timezone.datetime.strptime(end_date_str, "%d-%m-%Y %H:%M")
        except (Customer.DoesNotExist, Vehicle.DoesNotExist):
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "ID de cliente/vehículo inválido."}, status=HTTPStatus.BAD_REQUEST)
        except ValueError:
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Formato de fecha u hora incorrecto. Use DD-MM-YYYY HH:MM."}, status=HTTPStatus.BAD_REQUEST)

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
            end_date__gte=start_date,
            start_date__lte=end_date,
            status__in=['Activo', 'Reservado'],
            active=True
        )
        if conflicting_rentals.exists():
            errors.append("El vehículo no está disponible para las fechas seleccionadas.")
        if not vehicle.is_available:
            errors.append("El vehículo está actualmente marcado como no disponible en su estado general.")

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
            duration_days = (end_date.date() - start_date.date()).days + 1
            if duration_days <= 0:
                errors.append("La duración del alquiler debe ser al menos un día.")
            else:
                total_price = vehicle.daily_rate * decimal.Decimal(str(duration_days))

                required_initial_payment_percentage = 0.50 if duration_days <= 5 else 1.00
                required_initial_amount = total_price * decimal.Decimal(str(required_initial_payment_percentage))

                response_data['total_price_estimated'] = f"{total_price:.2f}"
                response_data['required_initial_payment'] = f"{required_initial_amount:.2f}"
                response_data['payment_percentage'] = required_initial_payment_percentage * 100
                response_data['deposit_required'] = decimal.Decimal('100.00') if customer.customer_type == 'extranjero' else decimal.Decimal('0.00')
                response_data['customer_type'] = customer.customer_type
                response_data['duration_days'] = duration_days
                response_data['vehicle_daily_rate'] = f"{vehicle.daily_rate:.2f}"
                response_data['customer_active_rentals'] = active_rentals_count

        if errors:
            response_data['errors'] = errors
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(response_data, status=HTTPStatus.BAD_REQUEST)

        # CAMBIADO: Usando JsonResponse y HTTPStatus
        return JsonResponse(response_data, status=HTTPStatus.OK)


class RentalFinalizeAPIView(APIView):
    """
    Endpoint para finalizar un alquiler existente.
    """
    @authenticate_user(required_permission='rental.change_rental')
    def post(self, request, pk):
        """
        Finaliza un alquiler, calculando recargos, gestionando pagos y generando facturas.
        """
        try:
            rental = Rental.objects.get(pk=pk, active=True)
        except Rental.DoesNotExist:
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Alquiler no encontrado o inactivo."}, status=HTTPStatus.NOT_FOUND)

        # Asumo que estos datos vienen del request.data desde el frontend
        payload_data = {
            'actual_return_date': request.data.get('actual_return_date'),
            'fuel_level_return': request.data.get('fuel_level_return'),
            'remarks': request.data.get('remarks', ''),
        }

        # Pasa el objeto rental al contexto del serializer
        serializer = RentalFinalizeSerializer(data=payload_data, context={'rental': rental})

        try:
            serializer.is_valid(raise_exception=True)
            user_id = request.user.id if request.user.is_authenticated else None
            finalized_rental = serializer.save(modified_by=user_id)

            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Alquiler finalizado con éxito.", "rental_id": finalized_rental.id}, status=HTTPStatus.OK)
        except Exception as e: # Cambiado de serializers.ValidationError a Exception
            if hasattr(e, 'detail'):
                # CAMBIADO: Usando JsonResponse y HTTPStatus
                return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": f"Ocurrió un error inesperado al finalizar el alquiler: {str(e)}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


class RentalAddPaymentAPIView(APIView):
    """
    Endpoint para añadir un pago a un alquiler existente.
    """
    @authenticate_user(required_permission='rental.add_payment')
    def post(self, request, pk):
        """
        Maneja la adición de un nuevo pago para un alquiler específico.
        """
        try:
            rental = Rental.objects.get(pk=pk, active=True)
        except Rental.DoesNotExist:
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": "Alquiler no encontrado o inactivo."}, status=HTTPStatus.NOT_FOUND) # Corregido NOT_NOTFOUND a NOT_FOUND

        payment_data = request.data.copy()
        payment_data['rental'] = rental.id
        if 'payment_date' not in payment_data:
            payment_data['payment_date'] = timezone.now()

        serializer = PaymentSerializer(data=payment_data)

        try:
            serializer.is_valid(raise_exception=True)
            user_id = request.user.id if request.user.is_authenticated else None
            serializer.save(created_by=user_id)

            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse(serializer.data, status=HTTPStatus.CREATED)
        except Exception as e: # Cambiado de serializers.ValidationError a Exception
            if hasattr(e, 'detail'):
                # CAMBIADO: Usando JsonResponse y HTTPStatus
                return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
            # CAMBIADO: Usando JsonResponse y HTTPStatus
            return JsonResponse({"detail": f"Error al registrar el pago: {str(e)}"}, status=HTTPStatus.BAD_REQUEST) # Corregido el cierre del paréntesis aquí
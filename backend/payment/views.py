# payment/views.py
from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus
import decimal
from django.db import transaction
from django.db.models import Sum

# Importa tus modelos
from payment.models import Payment
from rental.models import Rental # Necesario para actualizar el estado de la renta
from customer.models import Customer # Necesario para tipo de cliente en validaciones

# Importa tus serializadores
from payment.serializers import PaymentSerializer

# Importa tus decoradores y permisos personalizados
from utilities.decorators import authenticate_user

# Otras importaciones necesarias
from django.utils import timezone

# --- Vista para Listar y Crear Pagos ---
class PaymentRC(APIView):
    """
    Vista de API para listar (R, read) y crear (C, create) Pagos.
    """
    @authenticate_user(required_permission='payment.view_payment')
    def get(self, request):
        """
        Maneja las solicitudes GET para devolver una lista de todos los pagos activos.
        """
        try:
            # Puedes filtrar pagos por rental_id si lo pasas como parámetro de query
            rental_id = request.query_params.get('rental_id')
            if rental_id:
                payments = Payment.objects.filter(rental_id=rental_id, active=True).order_by('-payment_date')
            else:
                payments = Payment.objects.filter(active=True).order_by('-payment_date')
            
            serializer = PaymentSerializer(payments, many=True)
            return JsonResponse({
                "data": serializer.data
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )



    @authenticate_user(required_permission='payment.add_payment')
    def post(self, request):
        """
        Maneja las solicitudes POST para crear un nuevo pago.
        Realiza validaciones y actualiza el estado de la renta.
        """
        # Una transacción atómica asegura que si el pago no se registra,
        # la renta no cambie de estado, y viceversa.
        with transaction.atomic():
            serializer = PaymentSerializer(data=request.data, context={'request': request})
            try:
                serializer.is_valid(raise_exception=True)
                
                rental = serializer.validated_data['rental'] # La instancia de Rental validada por el serializer
                amount = serializer.validated_data['amount']
                concept = serializer.validated_data['concept']

                # Bloquear la instancia de la renta para evitar condiciones de carrera
                # Usamos select_for_update() en la renta para asegurarnos de que no haya cambios concurrentes
                rental = Rental.objects.select_for_update().get(id=rental.id)

                # --- Validaciones de Lógica de Negocio en la Vista (adicional a Serializer) ---
                # Esto es útil si necesitas acceso a más contexto o múltiples pagos
                total_rental_price = rental.total_price

                # Calcular duración en días (Duplicado de lógica para seguridad, podrías refactorizar)
                duration_total_seconds = (rental.end_date - rental.start_date).total_seconds()
                duration_days = int(duration_total_seconds / (24 * 3600))
                if duration_total_seconds % (24 * 3600) > 0 or duration_days == 0:
                    duration_days += 1

                # Porcentaje de pago inicial requerido
                required_initial_payment_percentage = decimal.Decimal('0.50')
                if duration_days > 5:
                    required_initial_payment_percentage = decimal.Decimal('1.00')
                
                expected_anticipo = total_rental_price * required_initial_payment_percentage
                expected_deposit = decimal.Decimal('100.00') if rental.customer.customer_type == 'extranjero' else decimal.Decimal('0.00')

                # Montos ya pagados de anticipo y depósito para esta renta
                paid_anticipo_so_far = Payment.objects.filter(
                    rental=rental,
                    concept='Anticipo',
                    active=True
                ).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')

                paid_deposit_so_far = Payment.objects.filter(
                    rental=rental,
                    concept='Deposito', # Asume que hay un concepto 'Deposito' para el depósito de garantía
                    active=True
                ).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')


                if concept == 'Anticipo':
                    if amount > expected_anticipo - paid_anticipo_so_far + decimal.Decimal('0.01'):
                        return JsonResponse(
                            {"detail": f"El monto del anticipo (${amount:.2f}) excede lo requerido (${expected_anticipo - paid_anticipo_so_far:.2f})."},
                            status=HTTPStatus.BAD_REQUEST
                        )
                elif concept == 'Deposito':
                    if rental.customer.customer_type != 'extranjero':
                        return JsonResponse(
                            {"detail": "No se requiere depósito para clientes nacionales."},
                            status=HTTPStatus.BAD_REQUEST
                        )
                    if amount > expected_deposit - paid_deposit_so_far + decimal.Decimal('0.01'):
                         return JsonResponse(
                            {"detail": f"El monto del depósito (${amount:.2f}) excede lo requerido (${expected_deposit - paid_deposit_so_far:.2f})."},
                            status=HTTPStatus.BAD_REQUEST
                        )
                
                # --- Guardar el Pago ---
                payment = serializer.save()

                # --- Lógica de Actualización del Estado de la Renta ---
                # Después de cada pago, verifica si los montos iniciales y de depósito se han cubierto.
                
                # Recalcular pagado_anticipo_so_far incluyendo el pago actual
                # (o si no, se asumiría que el pago actual ya se sumó al total después del save)
                current_total_anticipo = paid_anticipo_so_far + (amount if concept == 'Anticipo' else decimal.Decimal('0.00'))
                current_total_deposit = paid_deposit_so_far + (amount if concept == 'Deposito' else decimal.Decimal('0.00'))

                # Determinar si el pago inicial y el depósito están cubiertos
                anticipo_covered = current_total_anticipo >= expected_anticipo - decimal.Decimal('0.01') # Pequeña tolerancia
                deposit_covered = (expected_deposit == decimal.Decimal('0.00')) or (current_total_deposit >= expected_deposit - decimal.Decimal('0.01'))
                
                # Si ambos están cubiertos y la renta está 'Reservado', cámbiala a 'Activo'
                if anticipo_covered and deposit_covered and rental.status == 'Reservado':
                    rental.status = 'Activo'
                    rental.save()
                
                # --- Lógica para "Si la renta se creó pero no se hizo el pago, que se borre y el auto vuelva a estar disponible" ---
                # Esta lógica se manejará en el frontend (como lo tienes) haciendo un DELETE a la renta
                # si el usuario cierra el modal de pago o navega.
                # El backend no puede "saber" si el frontend no va a enviar un pago a menos que tengas un
                # proceso asíncrono (celery task) que revise rentas 'Reservado' sin pagos después de un tiempo.
                # Para el flujo actual, es el DELETE en RentalRetrieveUpdateDestroy el que gestiona esto.
                # Aquí, si el pago se hace, todo sigue normal. Si no se hace, el frontend debe llamar a DELETE.

                response_data = PaymentSerializer(payment).data
                return JsonResponse(response_data, status=HTTPStatus.CREATED)
            except Exception as e:
                # Si hay una excepción, la transacción se revierte automáticamente
                if hasattr(e, 'detail'):
                    return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
                return JsonResponse(
                    {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

# --- Vista para Recuperar, Actualizar y Eliminar un Pago Específico ---
class PaymentRetrieveUpdateDestroy(APIView):
    """
    Vista para operaciones de recuperación (R), actualización (U) y eliminación (D)
    de un solo pago por su ID.
    """
    @authenticate_user(required_permission='payment.view_payment')
    def get(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk, active=True)
            serializer = PaymentSerializer(payment)
            return JsonResponse(serializer.data, status=HTTPStatus.OK)
        except Payment.DoesNotExist:
            return JsonResponse({"detail": "Pago no encontrado."}, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    @authenticate_user(required_permission='payment.change_payment')
    def put(self, request, pk):
        with transaction.atomic():
            try:
                payment = Payment.objects.select_for_update().get(pk=pk, active=True) # Bloquea el pago
            except Payment.DoesNotExist:
                return JsonResponse({"detail": "Pago no encontrado."}, status=HTTPStatus.NOT_FOUND)

            serializer = PaymentSerializer(payment, data=request.data, partial=False, context={'request': request})
            try:
                serializer.is_valid(raise_exception=True)
                # Aquí puedes añadir lógica para verificar si el cambio de monto o concepto es válido
                # y cómo afecta a los totales de la renta.
                
                updated_payment = serializer.save()

                # Reevaluar el estado de la renta si el pago se actualiza
                # (esto puede ser complejo dependiendo de la lógica de pagos y reembolsos)
                # Por ahora, no hay lógica de reevaluación del estado de la renta en PUT,
                # ya que puede requerir recalcular todos los pagos de la renta.
                
                return JsonResponse(PaymentSerializer(updated_payment).data, status=HTTPStatus.OK)
            except Exception as e:
                if hasattr(e, 'detail'):
                    return JsonResponse(e.detail, status=HTTPStatus.BAD_REQUEST)
                return JsonResponse(
                    {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )

    @authenticate_user(required_permission='payment.delete_payment')
    def delete(self, request, pk):
        with transaction.atomic():
            try:
                payment = Payment.objects.select_for_update().get(pk=pk, active=True)
                rental = payment.rental # Obtén la renta asociada

                payment.active = False
                payment.modified_by = request.user.id if request.user.is_authenticated else None
                payment.save()

                # --- Lógica de Reevaluación del Estado de la Renta al Eliminar un Pago ---
                # Si se elimina un pago, la renta podría volver a 'Reservado' si ya no tiene el pago inicial.
                # Sumar todos los pagos activos restantes para la renta
                remaining_payments_total = Payment.objects.filter(
                    rental=rental, 
                    active=True, 
                    concept__in=['Anticipo', 'Cargo Adicional', 'Cargo por Retraso', 'Pago Final'] # Solo los que suman al total
                ).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')

                remaining_deposit_total = Payment.objects.filter(
                    rental=rental,
                    active=True,
                    concept='Deposito'
                ).aggregate(total=Sum('amount'))['total'] or decimal.Decimal('0.00')

                total_rental_price = rental.total_price
                duration_total_seconds = (rental.end_date - rental.start_date).total_seconds()
                duration_days = int(duration_total_seconds / (24 * 3600))
                if duration_total_seconds % (24 * 3600) > 0 or duration_days == 0:
                    duration_days += 1
                
                required_initial_payment_percentage = decimal.Decimal('0.50')
                if duration_days > 5:
                    required_initial_payment_percentage = decimal.Decimal('1.00')
                
                expected_anticipo = total_rental_price * required_initial_payment_percentage
                expected_deposit = decimal.Decimal('100.00') if rental.customer.customer_type == 'extranjero' else decimal.Decimal('0.00')

                anticipo_still_covered = remaining_payments_total >= expected_anticipo - decimal.Decimal('0.01')
                deposit_still_covered = (expected_deposit == decimal.Decimal('0.00')) or (remaining_deposit_total >= expected_deposit - decimal.Decimal('0.01'))

                if not anticipo_still_covered or not deposit_still_covered:
                    if rental.status == 'Activo': # Solo si estaba activo, lo vuelve a Reservado
                        rental.status = 'Reservado'
                        rental.save()
                # Considera si una renta 'Finalizado' con un pago eliminado debería volver a 'Activo'
                # Esto es una decisión de negocio más compleja.

                return JsonResponse({"detail": "Pago desactivado correctamente."}, status=HTTPStatus.NO_CONTENT)
            except Payment.DoesNotExist:
                return JsonResponse({"detail": "Pago no encontrado."}, status=HTTPStatus.NOT_FOUND)
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )
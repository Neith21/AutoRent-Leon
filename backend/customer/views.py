from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus
from django.db import transaction
import json
from django.core.exceptions import ValidationError

from customer.models import Customer
from customer.serializers import CustomerSerializer
from .forms import CustomerForm
from utilities.decorators import authenticate_user


class CustomerRC(APIView):
    """
    Vista de API para leer (R, read) y crear Clientes (C, create).
    Endpoint: http://192.168.1.6:8000/api/v1/customer
    Para probarlo en Postman necesitás haber creado una sesion en: http://192.168.1.6:8000/api/v1/user-control/login
    Luego tomar el token y ponerlo en el header de la petición get de este endpoint como: Authorization: Bearer eyJhbGciOi...
    """
    @authenticate_user(required_permission='customer.view_customer')
    def get(self, request):
        """
        Maneja las solicitudes GET para devolver una lista de todos los clientes activos.
        """
        try:
            data = Customer.objects.filter(active=True).order_by('last_name', 'first_name')
            serializer = CustomerSerializer(data, many=True)
            return JsonResponse({
                "data": serializer.data
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        
    
    @authenticate_user(required_permission='customer.add_customer')
    @transaction.atomic
    def post(self, request):
        user_id = request.user.id

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Cuerpo de la solicitud inválido."},
                status=HTTPStatus.BAD_REQUEST
            )

        form = CustomerForm(data)
        if form.is_valid():
            try:
                customer = form.save(commit=False)
                customer.created_by = user_id
                customer.modified_by = user_id
                customer.save()

                serializer = CustomerSerializer(customer)
                return JsonResponse({
                    "status": "success",
                    "message": "Cliente creado exitosamente.",
                    "data": serializer.data
                }, status=HTTPStatus.CREATED)
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Error interno al guardar el cliente: {e}"
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            error_message = "Datos inválidos. Por favor, corrija los errores."
            errors = form.errors.get_json_data()

            if '__all__' in errors: 
                error_message = errors['__all__'][0]['message']
            else:
                first_field_with_error = next(iter(errors))
                error_message = errors[first_field_with_error][0]['message']
                
            return JsonResponse({
                "status": "error",
                "message": error_message,
                "errors": form.errors
            }, status=HTTPStatus.BAD_REQUEST)
        
    
class CustomerRU(APIView):
    @authenticate_user(required_permission='customer.view_customer')
    def get(self, request, id):
        """
        Maneja las solicitudes GET para devolver los datos de un cliente específico.
        """
        try:
            customer = Customer.objects.get(pk=id, active=True)
            serializer = CustomerSerializer(customer)
            return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
        
        except Customer.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Cliente no encontrado o inactivo."
            }, status=HTTPStatus.NOT_FOUND)
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado al obtener el cliente: {e}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    

    @authenticate_user(required_permission='customer.change_customer')
    @transaction.atomic
    def put(self, request, id):
        """
        Maneja las solicitudes PUT para actualizar los datos de un cliente
        de forma parcial y manual, sin usar Django Forms.
        """
        user_id = request.user.id

        try:
            customer_instance = Customer.objects.get(pk=id, active=True)
        except Customer.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "No se puede actualizar. Cliente no encontrado o inactivo."
            }, status=HTTPStatus.NOT_FOUND)

        try:
            payload_data = json.loads(request.body)
            if not isinstance(payload_data, dict):
                raise ValueError("El cuerpo JSON debe ser un objeto.")
        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse(
                {"status": "error", "message": f"Cuerpo de la solicitud inválido: {str(e)}"},
                status=HTTPStatus.BAD_REQUEST
            )

        if not payload_data:
            return JsonResponse(
                {"status": "info", "message": "No se proporcionaron datos para actualizar."},
                status=HTTPStatus.BAD_REQUEST
            )

        updatable_fields = [
            'first_name', 'last_name', 'document_type', 'document_number',
            'address', 'phone', 'email', 'customer_type', 'birth_date',
            'status', 'reference', 'notes'
        ]
        has_changes = False

        for field, value in payload_data.items():
            if field not in updatable_fields:
                continue

            cleaned_value = value
            if isinstance(value, str):
                if field == 'email':
                    cleaned_value = value.lower().strip()
                else:
                    cleaned_value = value.strip()
            
            if getattr(customer_instance, field) != cleaned_value:
                setattr(customer_instance, field, cleaned_value)
                has_changes = True

        if not has_changes:
            return JsonResponse({
                "status": "info",
                "message": "No se detectaron cambios en los datos proporcionados."
            }, status=HTTPStatus.OK)

        customer_instance.modified_by = user_id

        try:
            fields_to_exclude = ['active', 'created_by', 'created_at', 'modified_by', 'updated_at']
            customer_instance.full_clean(exclude=fields_to_exclude)
        except ValidationError as e:
            return JsonResponse({
                "status": "error",
                "message": "Datos inválidos. Por favor, corrija los errores.",
                "errors": e.message_dict
            }, status=HTTPStatus.BAD_REQUEST)

        try:
            customer_instance.save()
            return JsonResponse({
                "status": "success",
                "message": "Cliente actualizado exitosamente."
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error interno al guardar la actualización: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


class CustomerD(APIView):
    
    @authenticate_user(required_permission='customer.delete_customer')
    @transaction.atomic
    def put(self, request, id):
        """
        Maneja las solicitudes PUT para desactivar un cliente específico.
        """
        user_id = request.user.id

        try:
            customer = Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Cliente no encontrado."
            }, status=HTTPStatus.NOT_FOUND)

        if not customer.active:
            return JsonResponse({
                "status": "info",
                "message": "El cliente ya se encuentra inactivo."
            }, status=HTTPStatus.OK)

        try:
            customer.active = False
            customer.modified_by = user_id
            
            customer.save(update_fields=['active', 'modified_by', 'updated_at'])

            return JsonResponse({
                "status": "success",
                "message": "Cliente desactivado exitosamente."
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado al desactivar el cliente: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
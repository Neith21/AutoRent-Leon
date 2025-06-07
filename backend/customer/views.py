from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus

from customer.models import Customer
from customer.serializers import CustomerSerializer
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
            # Obtiene todos los clientes activos, ordenados por apellido y nombre
            data = Customer.objects.filter(active=True).order_by('last_name', 'first_name')
            # Serializa los datos de los clientes
            serializer = CustomerSerializer(data, many=True)
            # Devuelve la respuesta en formato JSON
            return JsonResponse({
                "data": serializer.data
            }, status=HTTPStatus.OK)
        except Exception as e:
            # Manejo de errores genérico
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
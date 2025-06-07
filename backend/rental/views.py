from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus

from rental.models import Rental
from rental.serializers import RentalSerializer
from utilities.decorators import authenticate_user

class RentalRC(APIView):
    """
    Vista de API para leer (R, read) y crear Clientes (C, create).
    Endpoint: http://192.168.1.6:8000/api/v1/rental
    Para probarlo en Postman necesitás haber creado una sesion en: http://192.168.1.6:8000/api/v1/user-control/login
    Luego tomar el token y ponerlo en el header de la petición get de este endpoint como: Authorization: Bearer eyJhbGciOi...
    """
    @authenticate_user(required_permission='rental.view_rental')
    def get(self, request):
        """
        Maneja las solicitudes GET para devolver una lista de todos los alquileres activos.
        """
        try:
            # Optimización de consulta: select_related precarga los datos de las
            # claves foráneas en una sola consulta para evitar N+1 queries.
            data = Rental.objects.filter(active=True).select_related(
                'customer', 
                'vehicle', 
                'pickup_branch', 
                'return_branch'
            ).order_by('-start_date') # Ordena por los más recientes primero
            
            # Serializa los datos de los alquileres
            serializer = RentalSerializer(data, many=True)
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
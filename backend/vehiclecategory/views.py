from rest_framework.views import APIView
from django.http import JsonResponse, Http404
from http import HTTPStatus
from django.utils.timezone import now

from vehiclecategory.models import VehicleCategory
from vehiclecategory.serializers import VehicleCategorySerializer
from utilities.decorators import authenticate_user

# Create your views here.


class VehicleCategoryRC(APIView):
    

    @authenticate_user(required_permission='vehiclecategory.view_vehiclecategory')
    def get(self, request):


        try:
            # El usuario ya está autenticado y tiene los permisos necesarios en este punto
            data = VehicleCategory.objects.filter(active=True).order_by('id')
            datos_json = VehicleCategorySerializer(data, many=True)
            return JsonResponse({
                "data": datos_json.data
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

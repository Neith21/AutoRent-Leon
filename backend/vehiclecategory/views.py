from rest_framework.views import APIView
from django.http import JsonResponse, Http404
from http import HTTPStatus
from django.utils.timezone import now

from vehiclecategory.models import VehicleCategory
from vehiclecategory.serializers import VehicleCategorySerializer
from utilities.decorators import authenticate_user

# Create your views here.


class VehicleCategoryRC(APIView):
    

    @authenticate_user(required_permission='view_vehiclecategory')
    def get(self, request):


        # El usuario ya está autenticado y tiene los permisos necesarios en este punto
        data = VehicleCategory.objects.filter(active=True).order_by('id')
        datos_json = VehicleCategorySerializer(data, many=True)
        return JsonResponse({
            "data": datos_json.data
        }, status=HTTPStatus.OK)

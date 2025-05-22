from rest_framework.views import APIView
from django.http import JsonResponse, Http404
from http import HTTPStatus
from django.utils.timezone import now

from brand.models import Brand
from brand.serializers import BrandSerializer
from utilities.decorators import authenticate_user

# Create your views here.


class BrandRC(APIView):
    

    @authenticate_user(required_permission='view_brand')
    def get(self, request):


        # El usuario ya está autenticado y tiene los permisos necesarios en este punto
        data = Brand.objects.filter(active=True).order_by('id')
        datos_json = BrandSerializer(data, many=True)
        return JsonResponse({
            "data": datos_json.data
        }, status=HTTPStatus.OK)
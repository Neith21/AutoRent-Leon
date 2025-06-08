from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus
from django.db import transaction
import json

from .models import Brand
from .serializers import BrandSerializer
from .forms import BrandForm
from utilities.decorators import authenticate_user


# Create your views here.


class BrandRC(APIView):
    
    @authenticate_user(required_permission='brand.view_brand')
    def get(self, request):
        try:
            data = Brand.objects.filter(active=True).order_by('name')
            serializer = BrandSerializer(data, many=True)
            return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    @authenticate_user(required_permission='brand.add_brand')
    @transaction.atomic
    def post(self, request):
        user_id = request.user.id
        try:
            data_for_form = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Cuerpo de la solicitud inválido."},
                status=HTTPStatus.BAD_REQUEST
            )
        
        form = BrandForm(data_for_form)

        if form.is_valid():
            try:
                brand = form.save(commit=False)
                brand.created_by = user_id
                brand.modified_by = user_id
                brand.save()

                serializer = BrandSerializer(brand)
                return JsonResponse({
                    "status": "success",
                    "message": "Marca creada exitosamente.",
                    "data": serializer.data
                }, status=HTTPStatus.CREATED)
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Error interno al guardar la marca: {str(e)}"
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            error_message = form.errors.get('name', ["Datos inválidos."])[0]
            return JsonResponse({
                "status": "error",
                "message": error_message
            }, status=HTTPStatus.BAD_REQUEST)


class BrandRU(APIView):

    def get_object(self, id):
        try:
            return Brand.objects.get(pk=id)
        except Brand.DoesNotExist:
            return None

    @authenticate_user(required_permission='brand.view_brand')
    def get(self, request, id):
        brand = self.get_object(id)
        if not brand or not brand.active:
            return JsonResponse({
                "status": "error",
                "message": "Marca no encontrada o inactiva."
            }, status=HTTPStatus.NOT_FOUND)
        
        serializer = BrandSerializer(brand)
        return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)

    @authenticate_user(required_permission='brand.change_brand')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id
        brand_instance = self.get_object(id)

        if not brand_instance:
            return JsonResponse({
                "status": "error",
                "message": "Marca no encontrada."
            }, status=HTTPStatus.NOT_FOUND)

        try:
            payload_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Se esperaba un cuerpo JSON con los datos a actualizar."},
                status=HTTPStatus.BAD_REQUEST
            )
        
        form = BrandForm(payload_data, instance=brand_instance)

        if form.is_valid():
            if form.has_changed():
                try:
                    updated_brand = form.save(commit=False)
                    updated_brand.modified_by = user_id
                    updated_brand.save()
                    return JsonResponse({
                        "status": "success",
                        "message": "Marca actualizada exitosamente."
                    }, status=HTTPStatus.OK)
                except Exception as e:
                    return JsonResponse({
                        "status": "error",
                        "message": f"Error interno al actualizar la marca: {str(e)}"
                    }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                return JsonResponse({
                    "status": "info",
                    "message": "No se detectaron cambios en los datos proporcionados."
                }, status=HTTPStatus.OK)
        else:
            error_message = form.errors.get('name', ["Datos inválidos."])[0]
            return JsonResponse({
                "status": "error",
                "message": error_message
            }, status=HTTPStatus.BAD_REQUEST)


class BrandD(APIView):

    def get_object(self, id):
        try:
            return Brand.objects.get(pk=id)
        except Brand.DoesNotExist:
            return None

    @authenticate_user(required_permission='brand.delete_brand')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id
        brand = self.get_object(id)

        if not brand:
            return JsonResponse({
                "status": "error",
                "message": "Marca no encontrada."
            }, status=HTTPStatus.NOT_FOUND)

        if not brand.active:
            return JsonResponse({
                "status": "info",
                "message": "La marca ya se encuentra inactiva."
            }, status=HTTPStatus.OK)

        if brand.vehiclemodel_set.exists():
             return JsonResponse({
                "status": "error",
                "message": "No se puede desactivar la marca porque tiene modelos de vehículos asociados."
            }, status=HTTPStatus.CONFLICT)

        try:
            brand.active = False
            brand.modified_by = user_id
            brand.save(update_fields=['active', 'modified_by', 'updated_at'])
            return JsonResponse({
                "status": "success",
                "message": "Marca desactivada exitosamente."
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado al desactivar la marca: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
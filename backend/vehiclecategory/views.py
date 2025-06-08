from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus
from django.db import transaction
import json

from .models import VehicleCategory
from .serializers import VehicleCategorySerializer
from .forms import VehicleCategoryForm
from utilities.decorators import authenticate_user


# Create your views here.


class VehicleCategoryRC(APIView):
    
    @authenticate_user(required_permission='vehiclecategory.view_vehiclecategory')
    def get(self, request):
        try:
            categories = VehicleCategory.objects.filter(active=True).order_by('name')
            serializer = VehicleCategorySerializer(categories, many=True)
            return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud: {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    @authenticate_user(required_permission='vehiclecategory.add_vehiclecategory')
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
        
        form = VehicleCategoryForm(data_for_form)

        if form.is_valid():
            try:
                category = form.save(commit=False)
                category.created_by = user_id
                category.modified_by = user_id
                category.save()

                serializer = VehicleCategorySerializer(category)
                return JsonResponse({
                    "status": "success",
                    "message": "Categoría creada exitosamente.",
                    "data": serializer.data
                }, status=HTTPStatus.CREATED)
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Error interno al guardar la categoría: {str(e)}"
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            error_message = form.errors.get('name', ["Datos inválidos."])[0]
            return JsonResponse({
                "status": "error",
                "message": error_message
            }, status=HTTPStatus.BAD_REQUEST)


class VehicleCategoryRU(APIView):


    def get_object(self, id):
        try:
            return VehicleCategory.objects.get(pk=id)
        except VehicleCategory.DoesNotExist:
            return None

    @authenticate_user(required_permission='vehiclecategory.view_vehiclecategory')
    def get(self, request, id):
        category = self.get_object(id)
        if not category or not category.active:
            return JsonResponse({
                "status": "error",
                "message": "Categoría no encontrada o inactiva."
            }, status=HTTPStatus.NOT_FOUND)
        
        serializer = VehicleCategorySerializer(category)
        return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)

    @authenticate_user(required_permission='vehiclecategory.change_vehiclecategory')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id
        category_instance = self.get_object(id)

        if not category_instance:
            return JsonResponse({
                "status": "error",
                "message": "Categoría no encontrada."
            }, status=HTTPStatus.NOT_FOUND)

        try:
            payload_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Se esperaba un cuerpo JSON con los datos a actualizar."},
                status=HTTPStatus.BAD_REQUEST
            )
        
        form = VehicleCategoryForm(payload_data, instance=category_instance)

        if form.is_valid():
            if form.has_changed():
                try:
                    updated_category = form.save(commit=False)
                    updated_category.modified_by = user_id
                    updated_category.save()
                    return JsonResponse({
                        "status": "success",
                        "message": "Categoría actualizada exitosamente."
                    }, status=HTTPStatus.OK)
                except Exception as e:
                    return JsonResponse({
                        "status": "error",
                        "message": f"Error interno al actualizar la categoría: {str(e)}"
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


class VehicleCategoryD(APIView):

    def get_object(self, id):
        try:
            return VehicleCategory.objects.get(pk=id)
        except VehicleCategory.DoesNotExist:
            return None

    @authenticate_user(required_permission='vehiclecategory.delete_vehiclecategory')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id
        category = self.get_object(id)

        if not category:
            return JsonResponse({
                "status": "error",
                "message": "Categoría no encontrada."
            }, status=HTTPStatus.NOT_FOUND)

        if not category.active:
            return JsonResponse({
                "status": "info",
                "message": "La categoría ya se encuentra inactiva."
            }, status=HTTPStatus.OK)

        if category.vehicle_set.exists():
             return JsonResponse({
                 "status": "error",
                 "message": "No se puede desactivar la categoría porque tiene vehículos asociados."
             }, status=HTTPStatus.CONFLICT)

        try:
            category.active = False
            category.modified_by = user_id
            category.save(update_fields=['active', 'modified_by', 'updated_at'])
            return JsonResponse({
                "status": "success",
                "message": "Categoría desactivada exitosamente."
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado al desactivar la categoría: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
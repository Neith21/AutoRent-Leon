from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus
from django.db import transaction


from .models import VehicleModel
from brand.models import Brand
from .serializers import VehicleModelSerializer
from .forms import VehicleModelForm
from utilities.decorators import authenticate_user
from error_log import utils as error_log_utils

import json


class VehicleModelRC(APIView):

    @authenticate_user(required_permission='vehiclemodel.view_vehiclemodel')
    def get(self, request):
        try:
            data = VehicleModel.objects.select_related('brand').filter(active=True).order_by('brand__name', 'name')
            serializer = VehicleModelSerializer(data, many=True)
            return JsonResponse({
                "data": serializer.data
            }, status=HTTPStatus.OK)
        except Exception as e:
            error_log_utils.log_error(user=request.user, exception=e)
            return JsonResponse(
                {"status": "error", "message": "Ocurrió un error al procesar la solicitud."},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    @authenticate_user(required_permission='vehiclemodel.add_vehiclemodel')
    @transaction.atomic
    def post(self, request):
        user_id = request.user.id

        data_for_form = {}
        if hasattr(request, 'data') and isinstance(request.data, dict):
            data_for_form = request.data.copy()
        else:
            try:
                data_for_form = json.loads(request.body)
                if not isinstance(data_for_form, dict):
                    raise ValueError("El cuerpo JSON debe ser un objeto.")
            except (json.JSONDecodeError, ValueError) as e:
                error_log_utils.log_error(user=request.user, exception=e)
                return JsonResponse(
                    {"status": "error", "message": f"Cuerpo de la solicitud inválido: {str(e)}"},
                    status=HTTPStatus.BAD_REQUEST
                )
        
        if "brand_id" in data_for_form and "brand" not in data_for_form:
            data_for_form['brand'] = data_for_form.pop("brand_id")
        elif "brand" in data_for_form and not isinstance(data_for_form["brand"], Brand):
            pass 

        form = VehicleModelForm(data_for_form)
        if form.is_valid():
            try:
                vehicle_model = form.save(commit=False)
                vehicle_model.created_by = user_id
                vehicle_model.modified_by = user_id
                vehicle_model.active = True
                vehicle_model.save()

                serializer = VehicleModelSerializer(vehicle_model)
                return JsonResponse({
                    "status": "success",
                    "message": "Modelo de vehículo creado exitosamente.",
                    "data": serializer.data
                }, status=HTTPStatus.CREATED)
            except Exception as e:
                error_log_utils.log_error(user=request.user, exception=e)
                return JsonResponse({
                    "status": "error",
                    "message": "Error interno al guardar el modelo de vehículo."
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            found_specific_unique_error = False
            error_message_to_return = "Datos inválidos. Por favor, corrija los errores." 

            for field_key, error_list in form.errors.get_json_data().items():
                for error_detail in error_list:

                    if error_detail.get('code') == 'unique_together':
                        error_message_to_return = error_detail.get('message', "Ya existe un modelo con este nombre para la marca seleccionada.")
                        found_specific_unique_error = True
                        break
                if found_specific_unique_error:
                    break
            
            return JsonResponse({
                "status": "error",
                "message": error_message_to_return
            }, status=HTTPStatus.BAD_REQUEST)


class VehicleModelRU(APIView):

    @authenticate_user(required_permission='vehiclemodel.view_vehiclemodel')
    def get(self, request, id):
        try:
            vehicle_model = VehicleModel.objects.select_related('brand').get(pk=id, active=True)
            serializer = VehicleModelSerializer(vehicle_model)
            return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
        except VehicleModel.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Modelo de vehículo no encontrado o inactivo."
            }, status=HTTPStatus.NOT_FOUND)
        except Exception:
            return JsonResponse({
                "status": "error",
                "message": "Error inesperado al obtener el modelo."
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    @authenticate_user(required_permission='vehiclemodel.change_vehiclemodel')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id

        try:
            vehicle_model_instance = VehicleModel.objects.get(pk=id)
        except VehicleModel.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Modelo de vehículo no encontrado."
            }, status=HTTPStatus.NOT_FOUND)

        payload_data = {}
        if hasattr(request, 'data') and isinstance(request.data, dict):
            payload_data = request.data.copy()
        else:
            try:
                payload_data = json.loads(request.body)
                if not isinstance(payload_data, dict):
                    raise ValueError("El cuerpo JSON debe ser un objeto.")
            except (json.JSONDecodeError, ValueError) as e:
                error_log_utils.log_error(user=request.user, exception=e)
                return JsonResponse(
                    {"status": "error", "message": f"Se esperaba un cuerpo JSON con los datos a actualizar: {str(e)}"},
                    status=HTTPStatus.BAD_REQUEST
                )
        
        if not payload_data:
            return JsonResponse(
                {"status": "info", "message": "No se proporcionaron datos para actualizar."},
                status=HTTPStatus.BAD_REQUEST 
            )

        form_data = payload_data.copy()
        if "brand_id" in form_data and "brand" not in form_data :
            form_data['brand'] = form_data.pop("brand_id")

        form = VehicleModelForm(form_data, instance=vehicle_model_instance)

        if form.is_valid():
            if form.has_changed():
                try:
                    updated_model = form.save(commit=False)
                    updated_model.modified_by = user_id
                    updated_model.save() 
                    
                    return JsonResponse({
                        "status": "success",
                        "message": "Modelo de vehículo actualizado exitosamente.",
                    }, status=HTTPStatus.OK)
                except Exception as e:
                    error_log_utils.log_error(user=request.user, exception=e)
                    return JsonResponse({
                        "status": "error",
                        "message": "Error interno al guardar la actualización del modelo."
                    }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                return JsonResponse({
                    "status": "info",
                    "message": "No se detectaron cambios en los datos proporcionados. No se realizó ninguna actualización.",
                }, status=HTTPStatus.OK)
        else:
            found_specific_unique_error = False
            error_message_to_return = "Datos inválidos. Por favor, corrija los errores." 

            for field_key, error_list in form.errors.get_json_data().items():
                for error_detail in error_list:

                    if error_detail.get('code') == 'unique_together':
                        error_message_to_return = error_detail.get('message', "Ya existe un modelo con este nombre para la marca seleccionada.")
                        found_specific_unique_error = True
                        break
                if found_specific_unique_error:
                    break
            
            return JsonResponse({
                "status": "error",
                "message": error_message_to_return
            }, status=HTTPStatus.BAD_REQUEST)


class VehicleModelD(APIView):

    @authenticate_user(required_permission='vehiclemodel.delete_vehiclemodel')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id

        try:
            vehicle_model = VehicleModel.objects.get(pk=id)
        except VehicleModel.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Modelo de vehículo no encontrado."
            }, status=HTTPStatus.NOT_FOUND)

        if not vehicle_model.active:
            return JsonResponse({
                "status": "info",
                "message": "El modelo de vehículo ya está inactivo."
            }, status=HTTPStatus.OK)

        if vehicle_model.vehicle_set.exists():
             return JsonResponse({
                "status": "error",
                "message": "No se puede desactivar el modelo porque tiene vehículos asociados."
            }, status=HTTPStatus.CONFLICT)

        try:
            vehicle_model.active = False
            vehicle_model.modified_by = user_id
            vehicle_model.save(update_fields=['active', 'modified_by', 'updated_at'])

            return JsonResponse({
                "status": "success",
                "message": "Modelo de vehículo desactivado exitosamente."
            }, status=HTTPStatus.OK)
        except Exception as e:
            error_log_utils.log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado al desactivar el modelo de vehículo: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
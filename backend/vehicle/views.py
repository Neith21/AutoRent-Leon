from rest_framework.views import APIView
from django.http import JsonResponse
from http import HTTPStatus
from django.utils.timezone import now

from vehicle.models import Vehicle
from vehiclemodel.models import VehicleModel
from vehicleimage.models import VehicleImage
from vehicle.serializers import VehicleSerializer
from utilities.decorators import authenticate_user

from django.core.files.storage import FileSystemStorage
import os
from datetime import datetime

from .forms import VehicleForm
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
import json # Para parsear JSON body


def get_base_url():
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    port = os.getenv("BASE_URL_BACKEND_PORT")
    if port:
        return f"{base_url}:{port}"
    return base_url


class VehicleRC(APIView):
    @authenticate_user(required_permission='vehicle.view_vehicle')
    def get(self, request):
        try:
            data = Vehicle.objects.filter(active=True).order_by('id')
            serializer = VehicleSerializer(data, many=True)
            return JsonResponse({
                "data": serializer.data
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    @authenticate_user(required_permission='vehicle.add_vehicle')
    @transaction.atomic
    def post(self, request):
        user_id = request.user.id

        data_for_form = {}
        if hasattr(request, 'data') and isinstance(request.data, dict):
            for key, value in request.data.items():
                if not isinstance(value, UploadedFile) and \
                   not (isinstance(value, list) and value and isinstance(value[0], UploadedFile)):
                    data_for_form[key] = value
        else:
            try:
                body_data = json.loads(request.body)
                if isinstance(body_data, dict):
                    data_for_form = body_data
                else:
                    raise ValueError("El cuerpo JSON debe ser un objeto.")
            except (json.JSONDecodeError, ValueError) as e:
                return JsonResponse({"status": "error", "message": f"Cuerpo de la solicitud inválido: {e}"}, status=HTTPStatus.BAD_REQUEST)

        if "vehiclemodel_id" in data_for_form:
            data_for_form['vehiclemodel'] = data_for_form.pop("vehiclemodel_id")
        if "vehiclecategory_id" in data_for_form:
            data_for_form['vehiclecategory'] = data_for_form.pop("vehiclecategory_id")
        if "branch_id" in data_for_form:
            data_for_form['branch'] = data_for_form.pop("branch_id")

        form = VehicleForm(data_for_form, request.FILES)

        if form.is_valid():
            try:

                vehicle = form.save(commit=False)
                vehicle.created_by = user_id
                vehicle.modified_by = user_id
                vehicle.active = True
                
                vehicle.save()

                images = request.FILES.getlist("images")
                if images:
                    if len(images) > 6:
                        return JsonResponse( 
                            {"estado": "error", "mensaje": "Máximo 6 imágenes permitidas."},
                            status=HTTPStatus.BAD_REQUEST
                        )
                    
                    fs = FileSystemStorage()
                    
                    for img_index, img in enumerate(images):
                        if img.content_type not in ("image/png", "image/jpeg"):
                            return JsonResponse(
                                {"estado": "error", "mensaje": "Solo archivos PNG o JPEG son permitidos."},
                                status=HTTPStatus.BAD_REQUEST
                            )
                        
                        ext = os.path.splitext(img.name)[1].lower()
                        filename = f"vehicle_{vehicle.id}_{datetime.timestamp(datetime.now())}_{img_index}{ext}"
                        
                        try:
                            saved_path = fs.save(f"vehicle/{filename}", img) 
                            
                            VehicleImage.objects.create(
                                vehicle=vehicle,
                                vehicle_image=filename
                            )
                        except Exception as e_img:
                            return JsonResponse(
                                {"estado": "error", "mensaje": f"Error subiendo imagen '{img.name}': {str(e_img)}"},
                                status=HTTPStatus.INTERNAL_SERVER_ERROR
                            )
                
                return JsonResponse(
                    {"estado": "ok", "mensaje": "Vehículo creado exitosamente.", "vehicle_id": vehicle.id},
                    status=HTTPStatus.CREATED
                )
            
            except Exception as e_save:
                return JsonResponse(
                    {"estado": "error", "mensaje": f"Error interno al procesar la creación del vehículo: {str(e_save)}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR
                )
        else:
            return JsonResponse(
                {"estado": "error", "mensaje": "Datos inválidos. Por favor, corrija los errores.",
                 "detalles": form.errors.get_json_data(escape_html=True)},
                status=HTTPStatus.BAD_REQUEST
            )
    

class VehicleRU(APIView):
    @authenticate_user(required_permission='vehicle.view_vehicle')
    def get(self, request, id):
        try:
            vehicle = Vehicle.objects.select_related(
                'vehiclemodel', 
                'vehiclemodel__brand',
                'vehiclecategory',
                'branch'
            ).get(pk=id, active=True)

            vehicle_data = {
                "id": vehicle.id,
                "plate": vehicle.plate,
                "color": vehicle.color,
                "year": vehicle.year,
                "engine": vehicle.engine,
                "engine_type": vehicle.engine_type,
                "engine_number": vehicle.engine_number,
                "vin": vehicle.vin,
                "seat_count": vehicle.seat_count,
                "description": vehicle.description,
                "status": vehicle.status,
            }

            if vehicle.vehiclemodel:
                vehicle_data["vehiclemodel"] = {
                    "id": vehicle.vehiclemodel.id,
                    "name": vehicle.vehiclemodel.name,
                }
                if vehicle.vehiclemodel.brand:
                    vehicle_data["vehiclemodel"]["brand"] = {
                        "id": vehicle.vehiclemodel.brand.id,
                        "name": vehicle.vehiclemodel.brand.name,
                    }
                else:
                    vehicle_data["vehiclemodel"]["brand"] = None 
            else:
                vehicle_data["vehiclemodel"] = None

            if vehicle.vehiclecategory:
                vehicle_data["vehiclecategory"] = {
                    "id": vehicle.vehiclecategory.id,
                    "name": vehicle.vehiclecategory.name,
                }
            else:
                vehicle_data["vehiclecategory"] = None

            if vehicle.branch:
                vehicle_data["branch"] = {
                    "id": vehicle.branch.id,
                    "name": vehicle.branch.name,
                }
            else:
                vehicle_data["branch"] = None
            
            base_media_url = f"{get_base_url()}/uploads/vehicle/"
            images_data_list = []
            if hasattr(vehicle, 'images') and vehicle.images.exists():
                for img_instance in vehicle.images.all():
                    images_data_list.append({
                        "id": img_instance.id,
                        "url": f"{base_media_url}{img_instance.vehicle_image}"
                    })
            vehicle_data["images"] = images_data_list
            
            return JsonResponse({
                "data": vehicle_data
            }, status=HTTPStatus.OK)

        except Vehicle.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Vehículo no encontrado"
            }, status=HTTPStatus.NOT_FOUND)
        except AttributeError as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error al acceder a datos relacionados del vehículo: {e}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado procesando la solicitud: {e}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)   
        

    @authenticate_user(required_permission='vehicle.change_vehicle')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id

        try:
            vehicle = Vehicle.objects.get(pk=id)
        except Vehicle.DoesNotExist:
            return JsonResponse(
                {"estado": "error", "mensaje": "Vehículo no encontrado."},
                status=HTTPStatus.NOT_FOUND
            )
        
        if not hasattr(request, 'data') or not isinstance(request.data, dict):
            import json
            try:
                payload_data = json.loads(request.body)
                if not isinstance(payload_data, dict):
                    raise ValueError()
            except (json.JSONDecodeError, ValueError):
                return JsonResponse({"estado": "error", "mensaje": "Se esperaba un cuerpo JSON con los datos a actualizar."}, status=HTTPStatus.BAD_REQUEST)
        else:
            payload_data = request.data

        if not payload_data:
            return JsonResponse(
                {"estado": "info", "mensaje": "No se proporcionaron datos para actualizar."},
                status=HTTPStatus.BAD_REQUEST
            )

        updatable_fields = [
            'plate', 'vehiclemodel_id', 'vehiclecategory_id', 'branch_id' 'color', 'year',
            'engine', 'engine_type', 'engine_number', 'vin',
            'seat_count', 'description', 'status'
        ]

        cleaned_payload = {}
        for field_name, value in payload_data.items():
            if field_name not in updatable_fields:
                continue

            cleaned_value = value
            if isinstance(value, str):
                if field_name == 'plate': cleaned_value = value.upper().strip()
                elif field_name == 'vin': cleaned_value = value.upper().strip()
                elif field_name == 'color': cleaned_value = value.strip()
                elif field_name == 'engine_number': cleaned_value = value.strip()
                elif field_name in ['engine', 'description']: cleaned_value = value.strip()

            if field_name in ['year', 'seat_count'] and value is not None and value != '':
                try:
                    cleaned_value = int(value)
                except (ValueError, TypeError):
                    return JsonResponse(
                        {"estado": "error", "mensaje": f"Valor inválido para '{field_name}'. Se esperaba un número.",
                         "detalles": {field_name: [{"message": "Debe ser un número entero.", "code": "invalid_type"}]}},
                        status=HTTPStatus.BAD_REQUEST)
            
            cleaned_payload[field_name] = cleaned_value

        for field_name, value in cleaned_payload.items():
            if field_name == 'vehiclemodel_id':
                setattr(vehicle, 'vehiclemodel_id', value)
            elif field_name == 'vehiclecategory_id':
                setattr(vehicle, 'vehiclecategory_id', value)
            elif field_name == 'branch_id':
                setattr(vehicle, 'branch_id', value)
            else:
                setattr(vehicle, field_name, value)
        
        vehicle.modified_by = user_id

        try:
            vehicle.full_clean(exclude=['active', 'created_by', 'created_at', 'modified_by', 'updated_at'])
        except ValidationError as e:
            return JsonResponse(
                {"estado": "error", "mensaje": "Datos inválidos. Por favor, corrija los errores.",
                 "detalles": e.message_dict},
                status=HTTPStatus.BAD_REQUEST
            )
        try:
            vehicle.save()

            return JsonResponse(
                {"estado": "ok", "mensaje": "Vehículo actualizado exitosamente."},
                status=HTTPStatus.OK
            )
        except Exception as e_save:
            return JsonResponse(
                {"estado": "error", "mensaje": f"Error interno al guardar la actualización del vehículo: {str(e_save)}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

class VehicleD(APIView):
    @authenticate_user(required_permission='vehicle.delete_vehicle')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id

        try:
            vehicle = Vehicle.objects.get(pk=id)
        except Vehicle.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Vehículo no encontrado"
            }, status=HTTPStatus.NOT_FOUND)
            
        try:
            Vehicle.objects.filter(pk=id).update(
                active=False,
                modified_by=user_id,
                updated_at=now()
            )
            
            return JsonResponse({
                "status": "ok",
                "message": "Vehículo desactivado exitosamente"
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


class ModelsByBrandR(APIView):

    @authenticate_user(required_permission='vehicle.view_brand')
    def get(self, request, id):
        vehicle_models = VehicleModel.objects.filter(brand_id=id, active=True)

        if not vehicle_models.exists():
            return JsonResponse({
                "status": "error",
                "message": "Modelos no encontrados para esta marca"
            }, status=HTTPStatus.NOT_FOUND)

        data = [
            {"id": vm.id, "name": vm.name}
            for vm in vehicle_models
        ]

        return JsonResponse(
            {"data": data},
            status=HTTPStatus.OK
        )
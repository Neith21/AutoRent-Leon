from rest_framework.views import APIView
from django.http import JsonResponse, Http404
from http import HTTPStatus
from django.utils.timezone import now

from vehicle.models import Vehicle
from vehiclemodel.models import VehicleModel
from vehiclecategory.models import VehicleCategory
from vehicleimage.models import VehicleImage
from vehicle.serializers import VehicleSerializer
from utilities.decorators import authenticate_user
from jose import jwt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from datetime import datetime
from vehiclemodel.models import VehicleModel

from .forms import VehicleForm
from django.utils.timezone import now as django_now
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError

# Create your views here.

class VehicleRC(APIView):
    

    @authenticate_user(required_permission='view_vehicle')
    def get(self, request):


        # El usuario ya está autenticado y tiene los permisos necesarios en este punto
        data = Vehicle.objects.filter(active=True).order_by('id')
        datos_json = VehicleSerializer(data, many=True)
        return JsonResponse({
            "data": datos_json.data
        }, status=HTTPStatus.OK)
    
    
    @authenticate_user(required_permission='add_vehicle')
    @transaction.atomic
    def post(self, request):
        auth_header = request.headers.get("Authorization","").split()
        token_value = auth_header[1] if len(auth_header) == 2 else None
        user_id = None
        if token_value:
            try:
                decoded = jwt.decode(token_value, settings.SECRET_KEY, algorithms=["HS512"])
                user_id = decoded.get("id")
            except Exception:
                return JsonResponse(
                    {"estado": "error", "mensaje": "Token inválido o expirado."},
                    status=HTTPStatus.UNAUTHORIZED
                )
        else:
            return JsonResponse(
                {"estado": "error", "mensaje": "Token no proporcionado."},
                status=HTTPStatus.UNAUTHORIZED
            )
        if not user_id:
             return JsonResponse(
                {"estado": "error", "mensaje": "ID de usuario no encontrado en el token."},
                status=HTTPStatus.UNAUTHORIZED
            )
        
        data_for_form = {}
        if hasattr(request, 'data'):
            for key, value in request.data.items():
                if not isinstance(value, UploadedFile) and \
                   not (isinstance(value, list) and value and isinstance(value[0], UploadedFile)):
                    data_for_form[key] = value
        else:
            if request.POST:
                data_for_form = request.POST.copy()
            else:
                import json
                try:
                    body_data = json.loads(request.body)
                    if isinstance(body_data, dict):
                        data_for_form = body_data
                    else:
                        raise ValueError("El cuerpo JSON debe ser un objeto.")
                except (json.JSONDecodeError, ValueError) as e:
                    return JsonResponse({"estado": "error", "mensaje": f"Cuerpo de la solicitud inválido: {e}"}, status=HTTPStatus.BAD_REQUEST)

        # required_fields = [
        #     "plate", "vehiclemodel_id", "vehiclecategory_id",
        #     "color", "year", "engine_type", # "engine" es blank=True, "description" no está
        #     "engine_number", "vin", "seat_count", "status"
        # ]
        # error_validation = validate_required_fields(data_for_form, required_fields)
        # if error_validation:
        #     return error_validation # Asumo que devuelve un JsonResponse

        if "vehiclemodel_id" in data_for_form:
            data_for_form['vehiclemodel'] = data_for_form.pop("vehiclemodel_id")
        if "vehiclecategory_id" in data_for_form:
            data_for_form['vehiclecategory'] = data_for_form.pop("vehiclecategory_id")

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


    @authenticate_user(required_permission='view_vehicle')
    def get(self, request, id):
        try:
            vehicle = Vehicle.objects.select_related(
                'vehiclemodel', 
                'vehiclemodel__brand',
                'vehiclecategory'
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
            
            base_url_images = f"{os.getenv('BASE_URL')}:{os.getenv('BASE_URL_BACKEND_PORT')}/uploads/vehicle/"
            images_data_list = []
            if hasattr(vehicle, 'images') and vehicle.images.exists():
                for img_instance in vehicle.images.all():
                    images_data_list.append({
                        "id": img_instance.id,
                        "url": f"{base_url_images}{img_instance.vehicle_image}"
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
        

    @authenticate_user(required_permission='change_vehicle')
    @transaction.atomic
    def put(self, request, id):
        try:
            vehicle = Vehicle.objects.get(pk=id)
        except Vehicle.DoesNotExist:
            return JsonResponse(
                {"estado": "error", "mensaje": "Vehículo no encontrado."},
                status=HTTPStatus.NOT_FOUND
            )
        
        auth_header = request.headers.get("Authorization","").split()
        token_value = auth_header[1] if len(auth_header) == 2 else None
        user_id = None
        if token_value:
            try:
                decoded = jwt.decode(token_value, settings.SECRET_KEY, algorithms=["HS512"])
                user_id = decoded.get("id")
            except Exception:
                return JsonResponse(
                    {"estado": "error", "mensaje": "Token inválido o expirado."},
                    status=HTTPStatus.UNAUTHORIZED
                )
        else:
            return JsonResponse(
                {"estado": "error", "mensaje": "Token no proporcionado."},
                status=HTTPStatus.UNAUTHORIZED
            )
        if not user_id:
             return JsonResponse(
                {"estado": "error", "mensaje": "ID de usuario no encontrado en el token."},
                status=HTTPStatus.UNAUTHORIZED
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
            'plate', 'vehiclemodel_id', 'vehiclecategory_id', 'color', 'year',
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
    
    
    @authenticate_user(required_permission='change_vehicle')
    def put(self, request, id):


        try:
            vehicle = Vehicle.objects.get(pk=id)
        except Vehicle.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Vehículo no encontrado"
            }, status=HTTPStatus.NOT_FOUND)
        
        try:
            auth_header = request.headers.get("Authorization","").split()
            token = auth_header[1] if len(auth_header)==2 else None
            try:
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS512"])
                user_id = decoded.get("id")
            except Exception:
                return JsonResponse(
                    {"estado": "error", "mensaje": "Token inválido"},
                    status=HTTPStatus.UNAUTHORIZED
                )
            
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

    @authenticate_user(required_permission='view_brand')
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



def validate_required_fields(data, fields):
    for field in fields:
        value = data.get(field)
        if value is None:
            return JsonResponse({
                "status": "error",
                "message": f"The field '{field}' is required"
            }, status=HTTPStatus.BAD_REQUEST)
        if not str(value).strip():
            return JsonResponse({
                "status": "error",
                "message": f"The field '{field}' cannot be empty"
            }, status=HTTPStatus.BAD_REQUEST)
    return None
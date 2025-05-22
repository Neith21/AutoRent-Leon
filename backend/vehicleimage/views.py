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

# Create your views here.

BASE_IMAGE_URL = f"{os.getenv('BASE_URL')}:{os.getenv('BASE_URL_BACKEND_PORT')}/uploads/vehicle/"
MAX_IMAGES_PER_VEHICLE = 6

class VehicleImageCD(APIView):
    
    
    @authenticate_user(required_permission='change_vehicle')
    def post(self, request, id):
        try:
            vehicle = Vehicle.objects.get(pk=id, active=True)
        except Vehicle.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Vehículo no encontrado."
            }, status=HTTPStatus.NOT_FOUND)

        new_images_files = request.FILES.getlist("images")
        if not new_images_files:
            return JsonResponse({
                "status": "error",
                "message": "No se proporcionaron imágenes para subir."
            }, status=HTTPStatus.BAD_REQUEST)

        current_image_count = vehicle.images.count()
        
        if current_image_count + len(new_images_files) > MAX_IMAGES_PER_VEHICLE:
            return JsonResponse({
                "status": "error",
                "message": f"No se pueden añadir más imágenes. El límite es {MAX_IMAGES_PER_VEHICLE}. Actualmente tiene {current_image_count}."
            }, status=HTTPStatus.BAD_REQUEST)

        fs = FileSystemStorage()
        added_images_data = []

        auth_header = request.headers.get("Authorization","").split()
        token = auth_header[1] if len(auth_header)==2 else None
        user_id = None
        if token:
            try:
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS512"])
                user_id = decoded.get("id")
            except Exception:
                # Decidís si un token no válido debe bloquear la carga de la imagen o simplemente no registrar el user_id
                pass 

        for img_file in new_images_files:
            if img_file.content_type not in ("image/png", "image/jpeg"):
                return JsonResponse({
                    "status": "error",
                    "message": f"Tipo de archivo no permitido: {img_file.name}. Solo PNG o JPEG."
                }, status=HTTPStatus.BAD_REQUEST)

            ext = os.path.splitext(img_file.name)[1]
            filename = f"vehicle_{id}_{datetime.timestamp(datetime.now())}_{img_file.size}{ext}"
            
            try:
                saved_path = fs.save(f"vehicle/{filename}", img_file)
                
                vehicle_image_instance = VehicleImage.objects.create(
                    vehicle=vehicle,
                    vehicle_image=filename
                )
                added_images_data.append({
                    "id": vehicle_image_instance.id,
                    "url": f"{BASE_IMAGE_URL}{filename}"
                })
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Error subiendo la imagen {img_file.name}: {str(e)}"
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
        if user_id:
            vehicle.modified_by = user_id
        vehicle.updated_at = now()
        vehicle.save()

        return JsonResponse({
            "status": "ok",
            "message": "Imágenes añadidas exitosamente.",
            "added_images": added_images_data
        }, status=HTTPStatus.CREATED)

    @authenticate_user(required_permission='change_vehicle')
    def delete(self, request, id):
        try:
            vehicle_image_instance = VehicleImage.objects.get(pk=id)
        except VehicleImage.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Imagen no encontrada."
            }, status=HTTPStatus.NOT_FOUND)

        fs = FileSystemStorage()
        image_path_to_delete = f"vehicle/{vehicle_image_instance.vehicle_image}"

        try:
            if fs.exists(image_path_to_delete):
                fs.delete(image_path_to_delete)

            vehicle_image_instance.delete()

            vehicle = vehicle_image_instance.vehicle
            auth_header = request.headers.get("Authorization","").split()
            token = auth_header[1] if len(auth_header)==2 else None
            if token:
                try:
                    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS512"])
                    user_id = decoded.get("id")
                    if user_id:
                       vehicle.modified_by = user_id
                except Exception:
                    pass
            vehicle.updated_at = now()
            vehicle.save()

            return JsonResponse({
                "status": "ok",
                "message": "Imagen eliminada exitosamente."
            }, status=HTTPStatus.OK)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error eliminando la imagen: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
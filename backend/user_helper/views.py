from rest_framework.views import APIView
from django.http import JsonResponse, Http404
from http import HTTPStatus
from django.utils.text import slugify
from django.utils.dateformat import DateFormat
from dotenv import load_dotenv
from jose import jwt
from django.conf import settings
from django.contrib.auth.models import User, Permission
from simple_history.utils import update_change_reason
from django.contrib.auth import authenticate

#Editar user_image
from dotenv import load_dotenv
import os
from datetime import datetime
from django.core.files.storage import FileSystemStorage

from utilities.decorators import is_authenticated
from user_helper.serializers import *
from user_control.models import *
from error_log.utils import log_error
from utilities.decorators import authenticate_user

from rest_framework import status as drf_status

# Create your views here.


class UserR(APIView):
    
    @is_authenticated()
    def get(self, request):
        # El usuario ya está autenticado y tiene los permisos necesarios en este punto
        data = UsersMetadata.objects.filter(
            user__is_active=True
        ).order_by('id')
        datos_json = UserHelperSerializer(data, many=True)
        return JsonResponse({
            "data": datos_json.data
        }, status=HTTPStatus.OK)



class UserRU(APIView):
    
    #Este metodo no es para devolver un registro en base a su id, sino en base a un id foraneo contenido en ella, es distinta al tradicional
    @is_authenticated()
    def get(self, request, id):
        try:
            user = User.objects.filter(pk=id).get()

            instance = UsersMetadata.objects.get(user_id=id)
            serializer = UserHelperSerializer(instance)
            return JsonResponse({
                "data": serializer.data
            }, status=HTTPStatus.OK)

        except UsersMetadata.DoesNotExist as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "Resource not found"
            }, status=HTTPStatus.NOT_FOUND)


    @is_authenticated()
    def put(self, request, id):
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "User not found"
            }, status=HTTPStatus.NOT_FOUND)

        try:
            update_data = {}
            if "username" in request.data:
                update_data["username"] = request.data["username"]
            if "first_name" in request.data:
                update_data["first_name"] = request.data["first_name"]
            if "last_name" in request.data:
                update_data["last_name"] = request.data["last_name"]
            if "email" in request.data:
                update_data["email"] = request.data["email"]

            if update_data:
                User.objects.filter(pk=id).update(**update_data)
                return JsonResponse({
                    "status": "ok",
                    "message": "User successfully updated"
                }, status=HTTPStatus.OK)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "No valid fields provided"
                }, status=HTTPStatus.BAD_REQUEST)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": "Unexpected error occurred"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    

class EditImage(APIView):
    
    @is_authenticated()
    def post(self, request):
        # Validate required fields
        required_fields = ["id"]
        error = validate_required_fields(request.data, required_fields)
        if error:
            log_error(user=request.user, exception=Exception("All fields are required"))
            return error

        try:
            user_metadata = UsersMetadata.objects.get(user_id=request.data["id"])
            previous_image = user_metadata.user_image
        except UsersMetadata.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "User metadata not found"
            }, status=HTTPStatus.BAD_REQUEST)

        fs = FileSystemStorage()

        try:
            user_image = f"{datetime.timestamp(datetime.now())}{os.path.splitext(str(request.FILES['user_image']))[1]}"
        except Exception:
            return JsonResponse({
                "status": "error",
                "message": "An image file must be attached"
            }, status=HTTPStatus.BAD_REQUEST)

        if request.FILES["user_image"].content_type in ["image/jpeg", "image/png"]:
            try:
                fs.save(f"user/{user_image}", request.FILES['user_image'])
                fs.url(request.FILES['user_image'])
            except Exception:
                return JsonResponse({
                    "status": "error",
                    "message": "Failed to upload the image"
                }, status=HTTPStatus.BAD_REQUEST)

            try:
                UsersMetadata.objects.filter(user_id=request.data["id"]).update(user_image=user_image)

                # Remove the old image from the system
                if previous_image:
                    os.remove(f"./uploads/user/{previous_image}")

                return JsonResponse({
                    "status": "ok",
                    "message": "Image successfully updated"
                }, status=HTTPStatus.OK)
            except Exception:
                raise Http404

        else:
            return JsonResponse({
                "status": "error",
                "message": "user_image must be PNG or JPEG"
            }, status=HTTPStatus.BAD_REQUEST)
        

class UserD(APIView):

    @is_authenticated()
    def put(self, request, id):
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "User not found"
            }, status=HTTPStatus.NOT_FOUND)

        try:
            #User.objects.filter(pk=id).update(is_active=0)
            user._history_user = User.objects.get(id=id)  # Establecer quién hace el cambio
            user._change_reason = "desactivacion de usuario"
            user.is_active = 0                 # Desactivar el usuario
            user.save()                        # Guardar para registrar en el historial

            return JsonResponse({
                "status": "ok",
                "message": "User successfully deactivated"
            }, status=HTTPStatus.OK)

        except Exception as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "Unexpected error occurred"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        

class EditPassword(APIView):

    @is_authenticated()
    def post(self, request):
        # Validate required fields
        required_fields = ["id", "current_password", "new_password", "confirm_password"]
        error = validate_required_fields(request.data, required_fields)
        if error:
            log_error(user=request.user, exception=Exception("All fields are required"))
            return error
        
        # Extract data from request
        user_id = request.data.get("id")
        email = request.data.get("email")
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        
        # Validate new password matches confirmation
        if new_password != confirm_password:
            return JsonResponse({
                "status": "error",
                "message": "New password and confirmation do not match"
            }, status=HTTPStatus.BAD_REQUEST)
        
        try:
            # Get the user
            user = User.objects.filter(pk=user_id).get()
            
            auth = authenticate(request, username=email, password=current_password)
            if auth is not None:
                # Set new password
                user.set_password(new_password)
                user.save()
                
                return JsonResponse({
                    "status": "success",
                    "message": "Password updated successfully"
                }, status=HTTPStatus.OK)
        
            return JsonResponse({
                    "status": "error",
                    "message": "Current password is incorrect"
                }, status=HTTPStatus.BAD_REQUEST)
            
        except User.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "User not found"
            }, status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "An error occurred while updating the password"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        

class UserPermissionsView(APIView):

    @is_authenticated()
    def get(self, request):
        auth_header = request.headers.get('Authorization')

        token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS512'])

        user_id = decoded_token.get("id")
        if not user_id:
            return JsonResponse({
                "estado": "error",
                "mensaje": "Acceso no autorizado - ID de usuario no encontrado en el token"
            }, status=drf_status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                "estado": "error",
                "mensaje": "Acceso no autorizado - Usuario no encontrado"
            }, status=drf_status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return JsonResponse({
                "estado": "error",
                "mensaje": "Acceso no autorizado - Usuario inactivo"
            }, status=drf_status.HTTP_403_FORBIDDEN)

        if user.is_superuser:
            return JsonResponse({"permissions": True}, status=drf_status.HTTP_200_OK)
        else:
            user_permissions_set = user.get_all_permissions()

            permissions_list = sorted(list(user_permissions_set))
            
            return JsonResponse({"permissions": permissions_list}, status=drf_status.HTTP_200_OK)


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
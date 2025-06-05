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

from user_helper.serializers import *
from user_control.models import *
from error_log.utils import log_error
from utilities.decorators import authenticate_user
import re

from rest_framework import status as drf_status
from django.db import transaction

# Create your views here.


def validate_required_fields(data, fields):
    for field in fields:
        value = data.get(field)
        if value is None:
            return JsonResponse({
                "status": "error",
                "message": f"El campo '{field}' es requerido."
            }, status=HTTPStatus.BAD_REQUEST)
        if isinstance(value, str) and not value.strip():
            return JsonResponse({
                "status": "error",
                "message": f"El campo '{field}' no puede estar vacío."
            }, status=HTTPStatus.BAD_REQUEST)
    return None


def validate_password_complexity(password):
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return "La contraseña debe contener al menos una letra mayúscula."
    if not re.search(r"[a-z]", password):
        return "La contraseña debe contener al menos una letra minúscula."
    if not re.search(r"\d", password):
        return "La contraseña debe contener al menos un número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
         return "La contraseña debe contener al menos un carácter especial."
    return None


def validate_name_format(field, field_name):
    if not re.match(r"^[a-zA-ZÀ-ÿ\s'-]+$", field):
        return f"El campo '{field_name}' contiene caracteres no válidos. Solo se permiten letras y espacios."
    return None


class UserR(APIView):
    
    @authenticate_user()
    def get(self, request):
        try:
            # El usuario ya está autenticado y tiene los permisos necesarios en este punto
            data = UsersMetadata.objects.filter(
                user__is_active=True
            ).order_by('id')
            datos_json = UserHelperSerializer(data, many=True)
            return JsonResponse({
                "data": datos_json.data
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Ocurrió un error al procesar la solicitud. {e}"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )



class UserRU(APIView):
    
    #Este metodo no es para devolver un registro en base a su id, sino en base a un id foraneo contenido en ella, es distinta al tradicional
    @authenticate_user()
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
                "message": "Recurso no encontrado"
            }, status=HTTPStatus.NOT_FOUND)


    @authenticate_user()
    def put(self, request, id):
        try:
            user_to_update = User.objects.get(pk=id)
        except User.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Usuario no encontrado."
            }, status=HTTPStatus.NOT_FOUND)
        
        data = request.data
        update_fields_dict = {}
        validation_errors = {}

        if "first_name" in data:
            first_name = data["first_name"].strip()
            if not first_name:
                validation_errors["first_name"] = "El nombre no puede estar vacío."
            else:
                name_error = validate_name_format(first_name, "nombre")
                if name_error:
                    validation_errors["first_name"] = name_error
                else:
                    update_fields_dict["first_name"] = first_name

        if "last_name" in data:
            last_name = data["last_name"].strip()
            if last_name:
                name_error = validate_name_format(last_name, "apellido")
                if name_error:
                    validation_errors["last_name"] = name_error
                else:
                    update_fields_dict["last_name"] = last_name
            else:
                update_fields_dict["last_name"] = "" 

        if "username" in data:
            username = data["username"].strip()
            if not username:
                validation_errors["username"] = "El nombre de usuario no puede estar vacío."
            elif User.objects.filter(username=username).exclude(pk=user_to_update.id).exists():
                validation_errors["username"] = f"El nombre de usuario '{username}' ya está en uso."
            else:
                update_fields_dict["username"] = username

        if "email" in data:
            email = data["email"].strip().lower()
            if not email:
                validation_errors["email"] = "El correo electrónico no puede estar vacío."
            else:
                try:
                    from django.core.validators import validate_email
                    validate_email(email)
                    if User.objects.filter(email=email).exclude(pk=user_to_update.id).exists():
                        validation_errors["email"] = f"El correo electrónico '{email}' ya está en uso."
                    else:
                        update_fields_dict["email"] = email
                except Exception:
                    validation_errors["email"] = "El formato del correo electrónico no es válido."

        if validation_errors:
            return JsonResponse({
                "status": "error",
                "message": "Error de validación.",
                "errors": validation_errors
            }, status=HTTPStatus.BAD_REQUEST)

        if not update_fields_dict:
            return JsonResponse({
                "status": "info",
                "message": "No se proporcionaron campos válidos para actualizar."
            }, status=HTTPStatus.OK)

        try:
            with transaction.atomic():
                for field, value in update_fields_dict.items():
                    setattr(user_to_update, field, value)
                user_to_update.save(update_fields=update_fields_dict.keys())

                update_change_reason(user_to_update, f"Perfil actualizado por el usuario: {request.user.username}")

            return JsonResponse({
                "status": "ok",
                "message": "Perfil actualizado exitosamente."
            }, status=HTTPStatus.OK)

        except Exception as e:
            log_error(user=request.user, exception=e, additional_info=f"Error al actualizar perfil ID: {id}")
            return JsonResponse({
                "status": "error",
                "message": f"Ocurrió un error inesperado al actualizar el perfil: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    

class EditImage(APIView):
    
    @authenticate_user()
    def post(self, request):
        # Validate required fields
        required_fields = ["id"]
        error = validate_required_fields(request.data, required_fields)
        if error:
            log_error(user=request.user, exception=Exception("Todos los campos son obligatorios"))
            return error

        try:
            user_metadata = UsersMetadata.objects.get(user_id=request.data["id"])
            previous_image = user_metadata.user_image
        except UsersMetadata.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "No se encontraron metadatos del usuario"
            }, status=HTTPStatus.BAD_REQUEST)

        fs = FileSystemStorage()

        try:
            user_image = f"{datetime.timestamp(datetime.now())}{os.path.splitext(str(request.FILES['user_image']))[1]}"
        except Exception:
            return JsonResponse({
                "status": "error",
                "message": "Se debe adjuntar un archivo de imagen"
            }, status=HTTPStatus.BAD_REQUEST)

        if request.FILES["user_image"].content_type in ["image/jpeg", "image/png"]:
            try:
                fs.save(f"user/{user_image}", request.FILES['user_image'])
                fs.url(request.FILES['user_image'])
            except Exception:
                return JsonResponse({
                    "status": "error",
                    "message": "No se pudo cargar la imagen"
                }, status=HTTPStatus.BAD_REQUEST)

            try:
                UsersMetadata.objects.filter(user_id=request.data["id"]).update(user_image=user_image)

                # Remove the old image from the system
                if previous_image:
                    os.remove(f"./uploads/user/{previous_image}")

                return JsonResponse({
                    "status": "ok",
                    "message": "Imagen actualizada exitosamente"
                }, status=HTTPStatus.OK)
            except Exception:
                raise Http404

        else:
            return JsonResponse({
                "status": "error",
                "message": "La imagen del usuario debe ser PNG o JPEG"
            }, status=HTTPStatus.BAD_REQUEST)
        

class UserD(APIView):

    @authenticate_user(required_permission='user.delete_user')
    def put(self, request, id):
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "Usuario no encontrado"
            }, status=HTTPStatus.NOT_FOUND)

        try:
            #User.objects.filter(pk=id).update(is_active=0)
            user._history_user = User.objects.get(id=id)  # Establecer quién hace el cambio
            user._change_reason = "desactivacion de usuario"
            user.is_active = 0                 # Desactivar el usuario
            user.save()                        # Guardar para registrar en el historial

            return JsonResponse({
                "status": "ok",
                "message": "Usuario desactivada con éxito"
            }, status=HTTPStatus.OK)

        except Exception as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "Se produjo un error inesperado"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        

class EditPassword(APIView):

    @authenticate_user()
    def post(self, request):
        user_to_update = request.user
        data = request.data

        required_fields = ["current_password", "new_password", "confirm_password"]
        error_response = validate_required_fields(data, required_fields)
        if error_response:
            return error_response

        current_password = data.get("current_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        # Verificar contraseña actual
        if not user_to_update.check_password(current_password):
            return JsonResponse({
                "status": "error",
                "message": "La contraseña actual no es correcta."
            }, status=HTTPStatus.BAD_REQUEST)

        # Verificar que la nueva contraseña y la confirmación coincidan
        if new_password != confirm_password:
            return JsonResponse({
                "status": "error",
                "message": "La nueva contraseña y la confirmación no coinciden."
            }, status=HTTPStatus.BAD_REQUEST)
        
        # Verificar que la nueva contraseña no sea igual a la actual
        if user_to_update.check_password(new_password):
            return JsonResponse({
                "status": "error",
                "message": "La nueva contraseña no puede ser igual a la contraseña actual."
            }, status=HTTPStatus.BAD_REQUEST)

        # Validar complejidad de la nueva contraseña
        password_complexity_error = validate_password_complexity(new_password)
        if password_complexity_error:
            return JsonResponse({
                "status": "error",
                "message": password_complexity_error
            }, status=HTTPStatus.BAD_REQUEST)

        try:
            with transaction.atomic():
                user_to_update.set_password(new_password)
                user_to_update.save()

                update_change_reason(user_to_update, "Contraseña cambiada por el usuario.")

            return JsonResponse({
                "status": "ok",
                "message": "Contraseña actualizada exitosamente."
            }, status=HTTPStatus.OK)

        except Exception as e:
            log_error(user=request.user, exception=e, additional_info="Error al cambiar contraseña")
            return JsonResponse({
                "status": "error",
                "message": f"Ocurrió un error inesperado al cambiar la contraseña: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        

class UserPermissionsView(APIView):

    @authenticate_user()
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
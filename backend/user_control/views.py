from rest_framework.views import APIView
from django.http import JsonResponse, Http404, HttpResponseRedirect
from http import HTTPStatus
from django.contrib.auth.models import User #Django´s Model
import uuid
import os
from dotenv import load_dotenv
from django.contrib.auth import authenticate

#JWT
from jose import jwt
from django.conf import settings
from datetime import datetime, timedelta
import time


from .models import *
from utilities import utilities
#log_error es el que se encarga de guardar el error en la bitacora
from error_log.utils import log_error
#rollback
from django.db import transaction


# Create your views here.


class Register(APIView):
    def post(self, request):
        # Validate required fields
        required_fields = ["name", "email", "password"]
        error = validate_required_fields(request.data, required_fields)
        if error:
            log_error(user=request.user, exception=Exception(f"all fields are required"))
            return error

        if User.objects.filter(email=request.data["email"]).exists():
            log_error(user=request.user, exception=Exception(f"Attempt to register with an existing email: {request.data['email']}"))
            return JsonResponse({
                "status": "error",
                "message": f"The email {request.data['email']} is not available"
            }, status=HTTPStatus.CONFLICT)  # 409 Conflict

        token = uuid.uuid4()
        url = f"{os.getenv('BASE_URL')+':'+os.getenv('BASE_URL_BACKEND_PORT')}/api/v1/user-control/verification/{token}"

        try:
            # Uso de atomic para crear una transacción
            with transaction.atomic():
                user = User.objects.create_user(
                    username=request.data["email"],
                    password=request.data["password"],
                    email=request.data["email"],
                    first_name=request.data["name"],
                    last_name="",
                    is_active=0
                )

                # CAMBIO REALIZADO PARA FUNCIONAMIENTO DE LA BITACORA
                metadata = UsersMetadata.objects.create(token=token, user_id=user.id)
                history_record = metadata.history.last()
                history_record.history_user = user
                history_record.history_change_reason = "Creación de usuario, esperando verificación"
                history_record.save()

                html = f"""
                    <div style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 30px;">
                        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <h2 style="color: #333;">¡Verificación de cuenta!</h2>
                            <p style="font-size: 16px; color: #555;">
                                Hola <strong>{request.data["name"]}</strong>,
                            </p>
                            <p style="font-size: 16px; color: #555;">
                                Te has registrado exitosamente. Para activar tu cuenta, por favor haz clic en el siguiente botón:
                            </p>
                            <p style="text-align: center; margin: 30px 0;">
                                <a href="{url}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-size: 16px;">
                                    Activar cuenta
                                </a>
                            </p>
                            <p style="font-size: 14px; color: #777;">
                                Si el botón anterior no funciona, copia y pega el siguiente enlace en tu navegador:
                            </p>
                            <p style="font-size: 14px; word-break: break-all; color: #555;">{url}</p>
                            <hr style="margin: 40px 0;">
                            <p style="font-size: 12px; color: #aaa; text-align: center;">
                                Si no solicitaste esta cuenta, puedes ignorar este mensaje.
                            </p>
                        </div>
                    </div>
                """

                # Si falla el envío de correo, se lanzará una excepción y se revertirá la transacción
                utilities.sendMail(html, "Account Verification", request.data["email"])

            # Si llegamos aquí, es porque todo se completó correctamente
            return JsonResponse({
                "status": "ok",
                "message": "User successfully created"
            }, status=HTTPStatus.CREATED)

        except Exception as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "User could not be saved or email could not be sent"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


class Verification(APIView):

    def get(self, request, token):
        if token is None or not token:
            log_error(user=request.user, exception=Exception(f"Token is None or empty"))
            return JsonResponse({
                "status": "error",
                "message": "Resource not available"
            }, status=HTTPStatus.NOT_FOUND)

        try:
            data = UsersMetadata.objects.filter(token=token, user__is_active=0).get()

            # Invalidate the token - CAMBIOS REALIZADOS PARA FUNCIONAMIENTO DE LA BITACORA
            metadata = UsersMetadata.objects.get(token=token)
            metadata.token = ""
            metadata._history_user = data.user
            metadata._change_reason = "Token invalidado tras verificación"
            metadata.save()

            # Activate the user account
            User.objects.filter(id=data.user_id).update(is_active=1)

            # Redirect to frontend
            return HttpResponseRedirect(f"{os.getenv('BASE_URL')}:{os.getenv('BASE_URL_FRONTEND_PORT')}/autorent-leon/#/login")
            
        except UsersMetadata.DoesNotExist as e:
            log_error(user=request.user, exception=e)
            raise Http404("Verification token not found or already used.")

        except Exception as e:
            log_error(user=request.user, exception=e)
            raise Http404("Error during verification process.")  # O un 500 si quieres más técnico


class Login(APIView):

    def post(self, request):
        # Validate required fields
        required_fields = ["email", "password"]
        error = validate_required_fields(request.data, required_fields)
        if error:
            log_error(user=request.user, exception=Exception(f"all fields are required"))
            return error

        #No se puede hacer: SELECT * FROM auth_user WHERE correo = correo and password = password
        try:
            user = User.objects.filter(email=request.data["email"]).get()
        except User.DoesNotExist as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "Resource not found"
            }, status=HTTPStatus.NOT_FOUND)

        except Exception as e:
            log_error(user=request.user, exception=e)
            return JsonResponse({
                "status": "error",
                "message": "Resource not found"
            }, status=HTTPStatus.NOT_FOUND)

        #Este authenticate toma la contraseña normal y la compara con la encriptada, además ve si el usuario está activo
        auth = authenticate(request, username=request.data.get("email"), password=request.data.get("password"))
        if auth is not None:
            now = datetime.now()
            expiration = now + timedelta(days=1)
            expiration_timestamp = int(datetime.timestamp(expiration))
            
            payload = {
                "id": user.id,
                "name": user.first_name,
                "email": user.email,
                "is_superuser": user.is_superuser,
                "iss": os.getenv("BASE_URL")+':'+os.getenv('BASE_URL_BACKEND_PORT'),
                "iat": int(time.time()),
                "exp": expiration_timestamp
            }

            try:
                user.last_login = datetime.now()
                user.save(update_fields=['last_login'])

                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS512')
                return JsonResponse({
                    "token": token
                })
            except Exception as e:
                log_error(user=request.user, exception=e)
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid credentials"
                }, status=HTTPStatus.BAD_REQUEST)
        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid credentials"
            }, status=HTTPStatus.BAD_REQUEST)


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
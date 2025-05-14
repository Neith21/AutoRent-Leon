from functools import wraps
from django.http import JsonResponse
from http import HTTPStatus
from jose import jwt
from django.conf import settings
from django.contrib.auth.models import User
import time

def authenticate_user(required_permission=None):
    """
    Decorador que autentica al usuario y verifica si tiene el permiso requerido.
    
    Args:
        required_permission: String con el permiso requerido (opcional). Si es None,
                           solo verifica autenticación.
    """
    def decorator(func):
        @wraps(func)
        def _wrapped_view(request, *args, **kwargs):
            req = args[0]
            auth_header = req.headers.get('Authorization')
            if not auth_header:
                return JsonResponse({
                    "status": "error",
                    "message": "Unauthorized access - Missing Authorization header"
                }, status=HTTPStatus.UNAUTHORIZED)

            try:
                token = auth_header.split(" ")[1]
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS512'])
            except Exception:
                return JsonResponse({
                    "status": "error",
                    "message": "Unauthorized access - Invalid token"
                }, status=HTTPStatus.UNAUTHORIZED)

            if int(decoded.get("exp", 0)) <= int(time.time()):
                return JsonResponse({
                    "status": "error",
                    "message": "Unauthorized access - Token expired"
                }, status=HTTPStatus.UNAUTHORIZED)
            
            user_id = decoded.get("id")  # Corregido para usar "id" en lugar de "user_id"
            try:
                user = User.objects.get(id=user_id)
                
                # Si el usuario es superusuario, permitir acceso sin verificar permisos
                if user.is_superuser:
                    return func(request, *args, **kwargs)
                
                # Si se requiere un permiso específico, verificar que el usuario lo tenga
                if required_permission:
                    has_permission = False
                    
                    # Verificar permisos directos
                    for perm in user.user_permissions.all():
                        if perm.codename == required_permission:
                            has_permission = True
                            break
                    
                    # Verificar permisos de grupos si aún no se ha encontrado el permiso
                    if not has_permission:
                        for group in user.groups.all():
                            for perm in group.permissions.all():
                                if perm.codename == required_permission:
                                    has_permission = True
                                    break
                            if has_permission:
                                break
                    
                    if not has_permission:
                        return JsonResponse({
                            "status": "error",
                            "message": f"Forbidden - You don't have the required permission: {required_permission}"
                        }, status=HTTPStatus.FORBIDDEN)
                
                return func(request, *args, **kwargs)
                
            except User.DoesNotExist:
                return JsonResponse({
                    "status": "error",
                    "message": "Unauthorized access - User not found"
                }, status=HTTPStatus.UNAUTHORIZED)
            
        return _wrapped_view
    return decorator

def is_authenticated():
    def decorator(func):
        @wraps(func)
        def _wrapped_view(request, *args, **kwargs):
            req = args[0]
            auth_header = req.headers.get('Authorization')

            if not auth_header or auth_header == None:
                return JsonResponse({
                    "status": "error",
                    "message": "Unauthorized access - Missing Authorization header"
                }, status=HTTPStatus.UNAUTHORIZED)

            try:
                token = auth_header.split(" ")[1]
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS512'])
            except Exception:
                return JsonResponse({
                    "status": "error",
                    "message": "Unauthorized access - Invalid token"
                }, status=HTTPStatus.UNAUTHORIZED)

            if int(decoded.get("exp", 0)) > int(time.time()):
                return func(request, *args, **kwargs)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Unauthorized access - Token expired"
                }, status=HTTPStatus.UNAUTHORIZED)

        return _wrapped_view
    return decorator
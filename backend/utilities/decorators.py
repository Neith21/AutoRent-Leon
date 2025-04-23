from functools import wraps
from django.http import JsonResponse
from http import HTTPStatus
from jose import jwt
from django.conf import settings
import time

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

import os
import traceback
import inspect
import sys
from .models import ErrorLog

def log_error(user=None, exception=None):
    # Si el usuario es anónimo, lo dejamos como None
    if user and not user.is_authenticated:
        user = None

    # Intentamos extraer el traceback del error si existe
    tb = traceback.extract_tb(exception.__traceback__) if exception and exception.__traceback__ else []

    # Inicializamos valores por defecto
    filename = "unknown"
    lineno = 0
    function_name = "unknown"
    class_name = None

    if tb:
        first_call = tb[0]
        filename = os.path.basename(first_call.filename)
        lineno = first_call.lineno
        function_name = first_call.name
        frame = inspect.stack()[1]
    else:
        frame = inspect.stack()[1]
        filename = os.path.basename(frame.filename)
        lineno = frame.lineno
        function_name = frame.function

    # Verificamos si hay clase (por ejemplo en una View basada en clase)
    if 'self' in frame.frame.f_locals:
        class_name = type(frame.frame.f_locals['self']).__name__

    # Formato del método donde ocurrió el error
    method = f"File: {filename} - Class: {class_name if class_name else 'No class'} - Line: {lineno}"

    ErrorLog.objects.create(
        user=user,
        action=function_name,
        method=method,
        error_message=str(exception),
        stack_trace=traceback.format_exc() if tb else "No traceback available"
    )

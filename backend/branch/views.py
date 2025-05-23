from rest_framework.views import APIView
from django.http import JsonResponse, Http404
from http import HTTPStatus

from branch.models import Branch
from branch.serializers import BranchSerializer
from utilities.decorators import authenticate_user

from branch.forms import BranchForm
from django.conf import settings
from jose import jwt
from django.db import transaction
from django.core.exceptions import ValidationError
from district.models import District
from django.contrib.auth.models import User
from municipality.models import Municipality

# Create your views here.

def get_user_id_from_request(request):
    auth_header = request.headers.get("Authorization", "").split()
    token_value = auth_header[1] if len(auth_header) == 2 else None
    if not token_value:
        return None, JsonResponse(
            {"status": "error", "message": "Token no proporcionado."},
            status=HTTPStatus.UNAUTHORIZED
        )
    try:
        decoded = jwt.decode(token_value, settings.SECRET_KEY, algorithms=["HS512"])
        user_id = decoded.get("id")
        if not user_id:
            return None, JsonResponse(
                {"status": "error", "message": "ID de usuario no encontrado en el token."},
                status=HTTPStatus.UNAUTHORIZED
            )
        return user_id, None
    except Exception:
        return None, JsonResponse(
            {"status": "error", "message": "Token inválido o expirado."},
            status=HTTPStatus.UNAUTHORIZED
        )

class BranchRC(APIView):

    @authenticate_user(required_permission='view_branch')
    def get(self, request):
        data = Branch.objects.select_related(
            'district', 
            'district__municipality', 
            'district__municipality__department'
        ).filter(active=True).order_by('id')
        serializer = BranchSerializer(data, many=True)
        return JsonResponse({
            "data": serializer.data
        }, status=HTTPStatus.OK)

    @authenticate_user(required_permission='add_branch')
    @transaction.atomic
    def post(self, request):
        user_id, error_response = get_user_id_from_request(request)
        if error_response:
            return error_response

        data_for_form = {}
        if hasattr(request, 'data') and isinstance(request.data, dict):
            data_for_form = request.data.copy()
        else:
            if not isinstance(request.data, dict):
                 import json
                 try:
                    data_for_form = json.loads(request.body)
                    if not isinstance(data_for_form, dict):
                        raise ValueError("El cuerpo JSON debe ser un objeto.")
                 except (json.JSONDecodeError, ValueError) as e:
                    return JsonResponse({"status": "error", "message": f"Cuerpo de la solicitud inválido: {e}"}, status=HTTPStatus.BAD_REQUEST)

        if "district_id" in data_for_form:
            data_for_form['district'] = data_for_form.pop("district_id")
        elif "district" in data_for_form and not isinstance(data_for_form["district"], District):
            pass


        form = BranchForm(data_for_form)
        if form.is_valid():
            try:
                branch = form.save(commit=False)
                branch.created_by = user_id
                branch.modified_by = user_id 
                branch.active = True
                branch.save()

                serializer = BranchSerializer(branch)
                return JsonResponse({
                    "status": "success",
                    "message": "Sucursal creada exitosamente.",
                    "data": serializer.data
                }, status=HTTPStatus.CREATED)
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Error interno al guardar la sucursal: {str(e)}"
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            return JsonResponse({
                "status": "error",
                "message": "Datos inválidos. Por favor, corrija los errores.",
                "details": form.errors.get_json_data(escape_html=True)
            }, status=HTTPStatus.BAD_REQUEST)


class BranchRU(APIView):

    @authenticate_user(required_permission='view_branch')
    def get(self, request, id):
        try:
            branch = Branch.objects.select_related(
                'district', 
                'district__municipality', 
                'district__municipality__department'
            ).get(pk=id, active=True)

            branch_data = {
                "id": branch.id,
                "name": branch.name,
                "phone": branch.phone,
                "address": branch.address,
                "email": branch.email,
                "district_id": branch.district_id,
            }

            if branch.district:
                district_info = {
                    "id": branch.district.id,
                    "name": branch.district.district, 
                    "code": branch.district.code, 
                }
                if branch.district.municipality:
                    municipality_info = {
                        "id": branch.district.municipality.id,
                        "name": branch.district.municipality.municipality,
                        "code": branch.district.municipality.code, 
                    }
                    if branch.district.municipality.department:
                        department_info = {
                            "id": branch.district.municipality.department.id,
                            "name": branch.district.municipality.department.department,
                            "code": branch.district.municipality.department.code,
                        }
                        municipality_info["department"] = department_info
                    else:
                        municipality_info["department"] = None
                    district_info["municipality"] = municipality_info
                else:
                    district_info["municipality"] = None
                branch_data["district_details"] = district_info
            else:
                branch_data["district_details"] = None

            return JsonResponse({
                "data": branch_data
            }, status=HTTPStatus.OK)

        except Branch.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Sucursal no encontrada o inactiva."
            }, status=HTTPStatus.NOT_FOUND)
        except AttributeError as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error al acceder a datos relacionados: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        

    @authenticate_user(required_permission='change_branch')
    @transaction.atomic
    def put(self, request, id):
        user_id, error_response = get_user_id_from_request(request)
        if error_response:
            return error_response

        try:
            branch_instance = Branch.objects.get(pk=id)
        except Branch.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Sucursal no encontrada."
            }, status=HTTPStatus.NOT_FOUND)

        payload_data = {}
        if hasattr(request, 'data') and isinstance(request.data, dict):
            payload_data = request.data.copy()
        else:
            import json
            try:
                payload_data = json.loads(request.body)
                if not isinstance(payload_data, dict):
                    raise ValueError("El cuerpo JSON debe ser un objeto.")
            except (json.JSONDecodeError, ValueError):
                return JsonResponse({"status": "error", "message": "Se esperaba un cuerpo JSON con los datos a actualizar."}, status=HTTPStatus.BAD_REQUEST)

        if not payload_data:
            return JsonResponse(
                {"status": "info", "message": "No se proporcionaron datos para actualizar."},
                status=HTTPStatus.BAD_REQUEST
            )

        updatable_fields_from_payload = ['name', 'phone', 'address', 'district_id', 'email']
        has_changes = False

        for field_key_in_payload, value in payload_data.items():
            if field_key_in_payload not in updatable_fields_from_payload:
                continue

            actual_model_field_name = field_key_in_payload
            cleaned_value = value

            if field_key_in_payload == "district_id":
                actual_model_field_name = "district_id" 
                if value is None or str(value).strip() == '':
                    cleaned_value = None
                else:
                    try:
                        cleaned_value = int(value)
                    except (ValueError, TypeError):
                        return JsonResponse(
                            {"status": "error", "message": f"Valor inválido para 'district_id'. Se esperaba un número entero o nulo."},
                            status=HTTPStatus.BAD_REQUEST)
            elif isinstance(value, str):
                if field_key_in_payload == 'name': cleaned_value = value.strip()
                elif field_key_in_payload == 'phone': cleaned_value = value.strip()
                elif field_key_in_payload == 'address': cleaned_value = value.strip()
                elif field_key_in_payload == 'email': cleaned_value = value.lower().strip()
            
            if hasattr(branch_instance, actual_model_field_name):
                if getattr(branch_instance, actual_model_field_name) != cleaned_value:
                    setattr(branch_instance, actual_model_field_name, cleaned_value)
                    has_changes = True
            elif actual_model_field_name == "district_id":
                 if branch_instance.district_id != cleaned_value:
                    branch_instance.district_id = cleaned_value
                    has_changes = True

        if not has_changes:
             return JsonResponse({
                 "status": "info",
                 "message": "No se detectaron cambios en los datos proporcionados."
             }, status=HTTPStatus.OK)

        branch_instance.modified_by = user_id

        try:
            fields_to_exclude_from_full_clean = ['created_by', 'created_at', 'modified_by', 'active']
            branch_instance.full_clean(exclude=fields_to_exclude_from_full_clean)
        except ValidationError as e:
            return JsonResponse({
                "status": "error",
                "message": "Datos inválidos. Por favor, corrija los errores.",
                "details": e.message_dict
            }, status=HTTPStatus.BAD_REQUEST)

        try:
            branch_instance.save()

            return JsonResponse({
                "status": "success",
                "message": "Sucursal actualizada exitosamente.",
            }, status=HTTPStatus.OK)
        except Exception as e_save:
            return JsonResponse({
                "status": "error",
                "message": f"Error interno al guardar la actualización de la sucursal: {str(e_save)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


class BranchD(APIView):

    @authenticate_user(required_permission='change_branch')
    @transaction.atomic
    def put(self, request, id):
        user_id, error_response = get_user_id_from_request(request)
        if error_response:
            return error_response

        try:
            branch = Branch.objects.get(pk=id)
        except Branch.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Sucursal no encontrada."
            }, status=HTTPStatus.NOT_FOUND)

        try:
            branch.active = False
            branch.modified_by = user_id
            # branch.updated_at se actualiza por auto_now=True al llamar a save()
            branch.save() 

            return JsonResponse({
                "status": "success",
                "message": "Sucursal desactivada exitosamente."
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Error inesperado al desactivar la sucursal: {str(e)}"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        

class MunicipalitiesByDepartmentR(APIView):

    @authenticate_user(required_permission='view_municipality')
    def get(self, request, id):
        try:
            dept_id = int(id)
        except ValueError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid department ID format."
            }, status=HTTPStatus.BAD_REQUEST)

        municipalities = Municipality.objects.filter(department_id=dept_id, active=True).order_by('code')

        if not municipalities.exists():
            return JsonResponse({
                "status": "error",
                "message": "No municipalities found for this department or department does not exist."
            }, status=HTTPStatus.NOT_FOUND)

        data = [
            {"id": m.id, "name": m.municipality}
            for m in municipalities
        ]

        return JsonResponse({
            "data": data
        }, status=HTTPStatus.OK)



class DistrictsByMunicipalityR(APIView):

    @authenticate_user(required_permission='view_district')
    def get(self, request, id):
        try:
            mun_id = int(id)
        except ValueError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid municipality ID format."
            }, status=HTTPStatus.BAD_REQUEST)

        districts = District.objects.filter(municipality_id=mun_id, active=True).order_by('code')

        if not districts.exists():
            return JsonResponse({
                "status": "error",
                "message": "No districts found for this municipality or municipality does not exist."
            }, status=HTTPStatus.NOT_FOUND)

        data = [
            {"id": d.id, "name": d.district}
            for d in districts
        ]

        return JsonResponse({
            "data": data
        }, status=HTTPStatus.OK)
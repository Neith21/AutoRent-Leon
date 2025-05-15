from rest_framework.views import APIView
from django.http import JsonResponse, Http404
from http import HTTPStatus
from django.utils.timezone import now

from branch.models import Branch
from branch.serializers import BranchSerializer
from utilities.decorators import authenticate_user

# Create your views here.
class BranchRC(APIView):
    

    @authenticate_user(required_permission='view_branch')
    def get(self, request):
        # El usuario ya está autenticado y tiene los permisos necesarios en este punto
        data = Branch.objects.filter(active=True).order_by('id')
        datos_json = BranchSerializer(data, many=True)
        return JsonResponse({
            "data": datos_json.data
        }, status=HTTPStatus.OK)

    @authenticate_user(required_permission='add_branch')
    def post(self, request):

        # Validar campos requeridos
        required_fields = ['name', 'phone', 'address', 'department', 'district', 'email']

        validation_error = validate_required_fields(request.data, required_fields)
        if validation_error:
            return validation_error

        # Crear la sucursal
        try:
            branch = Branch.objects.create(
                name=request.data['name'].strip(),
                phone=request.data['phone'].strip(),
                address=request.data['address'].strip(),
                department=request.data['department'].strip(),
                district=request.data['district'].strip(),
                email=request.data['email'].strip(),
                active=True,
                created_by=request.data['userc'],
                modified_by=request.data['useru'],
                created_at=now(),
                updated_at=now()
            )

            return JsonResponse({
                "status": "success",
                "message": "Branch created successfully",
                "data": {
                    "id": branch.id,
                    "name": branch.name
                }
            }, status=HTTPStatus.CREATED)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


class BranchRU(APIView):
    

    @authenticate_user(required_permission='view_branch')
    def get(self, request, id):
        try:
            branch = Branch.objects.get(pk=id, active=True)
            serializer = BranchSerializer(branch)
            return JsonResponse({
                "data": serializer.data
            }, status=HTTPStatus.OK)

        except Branch.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Branch not found"
            }, status=HTTPStatus.NOT_FOUND)


    @authenticate_user(required_permission='change_branch')
    def put(self, request, id):
        try:
            branch = Branch.objects.get(pk=id)
        except Branch.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Branch not found"
            }, status=HTTPStatus.NOT_FOUND)

        try:
            update_data = {}

            if "name" in request.data:
                update_data["name"] = request.data["name"].strip()
            if "phone" in request.data:
                update_data["phone"] = request.data["phone"].strip()
            if "address" in request.data:
                update_data["address"] = request.data["address"].strip()
            if "department" in request.data:
                update_data["department"] = request.data["department"].strip()
            if "district" in request.data:
                update_data["district"] = request.data["district"].strip()
            if "email" in request.data:
                update_data["email"] = request.data["email"].strip()
            if "useru" in request.data:
                update_data["modified_by"] = request.data["useru"]

            # Actualizar la fecha de modificación
            update_data["updated_at"] = now()

            if update_data:
                Branch.objects.filter(pk=id).update(**update_data)
                return JsonResponse({
                    "status": "ok",
                    "message": "Branch successfully updated"
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


class BranchD(APIView):
    

    @authenticate_user(required_permission='change_branch')
    def put(self, request, id):
        try:
            branch = Branch.objects.get(pk=id)
        except Branch.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Branch not found"
            }, status=HTTPStatus.NOT_FOUND)

        try:
            Branch.objects.filter(pk=id).update(active=False)

            return JsonResponse({
                "status": "ok",
                "message": "Branch successfully deactivated"
            }, status=HTTPStatus.OK)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": "Unexpected error occurred"
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


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
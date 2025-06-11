from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Company
from .serializers import CompanySerializer
from utilities.decorators import authenticate_user

import cloudinary
import cloudinary.uploader


class CompanyRU(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @authenticate_user(required_permission='company.view_company')
    def get(self, request):
        company = Company.objects.first()
        if not company:
            return Response(
                {"status": "error", "message": "No se ha configurado la información de la empresa."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CompanySerializer(company)
        return Response({"status": "success", "data": serializer.data})

    @authenticate_user(required_permission='company.change_company')
    def patch(self, request, *args, **kwargs):
        instance = Company.objects.first()
        if not instance:
            return Response({"status": "error", "message": "No hay una empresa para actualizar."}, status=status.HTTP_404_NOT_FOUND)

        if 'logo' in request.FILES:
            new_logo_file = request.FILES['logo']

            if instance.logo_public_id:
                try:
                    cloudinary.uploader.destroy(instance.logo_public_id)
                except Exception as e:
                    print(f"Error borrando logo antiguo de Cloudinary: {e}")

            try:
                upload_result = cloudinary.uploader.upload(new_logo_file, folder="company_logos")
            except Exception as e:
                 return Response({"status": "error", "message": f"Error al subir el logo: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            instance.logo = upload_result.get('secure_url')
            instance.logo_public_id = upload_result.get('public_id')
            
            original_url = instance.logo
            if original_url:
                instance.logo_lqip = original_url.replace('/upload/', '/upload/w_200/e_blur:100/q_auto:low/')
            else:
                instance.logo_lqip = None

        serializer = CompanySerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            updated_company = serializer.save()

            return Response({
                "status": "success",
                "message": "La información de la empresa ha sido actualizada.",
                "data": CompanySerializer(updated_company).data
            })

        return Response({
            "status": "error",
            "message": "Datos inválidos.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import serializers
from customer.models import Customer
from django.contrib.auth.models import User

class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Customer.

    Este serializador convierte las instancias del modelo Customer en un formato JSON,
    listo para ser utilizado en una API. Incluye campos para los nombres de los usuarios
    de auditoría y formatea las fechas para una mejor presentación.
    """

    # --- Campos de Auditoría Personalizados ---
    created_by_name = serializers.SerializerMethodField(read_only=True)
    modified_by_name = serializers.SerializerMethodField(read_only=True)

    # --- Formateo de Fechas ---
    created_at = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    birth_date = serializers.DateField(format="%d-%m-%Y")

    class Meta:
        model = Customer
        # Lista de campos que se incluirán en la respuesta JSON.
        fields = (
            "id",
            "first_name",
            "last_name",
            "document_type",
            "document_number",
            "address",
            "phone",
            "email",
            "customer_type",
            "birth_date",
            "status",
            "reference",
            "notes",
            "active",
            "created_by",
            "created_by_name",
            "created_at",
            "modified_by",
            "modified_by_name",
            "updated_at"
        )

    def get_created_by_name(self, obj):
        """
        Obtiene el 'first_name' del usuario que creó el cliente.
        """
        if obj.created_by is None:
            return None
        try:
            user = User.objects.get(id=obj.created_by)
            return user.first_name
        except (User.DoesNotExist, ValueError):
            return None

    def get_modified_by_name(self, obj):
        """
        Obtiene el 'first_name' del usuario que modificó el cliente por última vez.
        """
        if obj.modified_by is None:
            return None
        try:
            user = User.objects.get(id=obj.modified_by)
            return user.first_name
        except (User.DoesNotExist, ValueError):
            return None

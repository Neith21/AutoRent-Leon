from rest_framework import serializers
from rental.models import Rental
from django.contrib.auth.models import User

class RentalSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Rental.

    Transforma las instancias de Rental a formato JSON. Incluye detalles
    de los modelos relacionados (Cliente, Vehículo, Sucursal) para una
    respuesta más completa y legible.
    """

    # --- Campos de Modelos Relacionados (para lectura) ---
    customer_name = serializers.CharField(source='customer.__str__', read_only=True) # Aquí podes ponerle source='customer.first_name' para obtener el nombre
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    pickup_branch_name = serializers.CharField(source='pickup_branch.name', read_only=True)
    return_branch_name = serializers.CharField(source='return_branch.name', read_only=True)

    # --- Campos de Auditoría Personalizados ---
    created_by_name = serializers.SerializerMethodField(read_only=True)
    modified_by_name = serializers.SerializerMethodField(read_only=True)

    # --- Formateo de Fechas (incluyendo hora) ---
    start_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    end_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    actual_return_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    class Meta:
        model = Rental
        fields = (
            "id",
            "customer", # ID del cliente
            "customer_name",
            "vehicle", # ID del vehículo
            "vehicle_plate",
            "pickup_branch", # ID de sucursal de recogida
            "pickup_branch_name",
            "return_branch", # ID de sucursal de devolución
            "return_branch_name",
            "start_date",
            "end_date",
            "actual_return_date",
            "status",
            "total_price",
            "fuel_level_pickup",
            "fuel_level_return",
            "remarks",
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
        Obtiene el 'first_name' del usuario que creó el alquiler.
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
        Obtiene el 'first_name' del usuario que modificó el alquiler por última vez.
        """
        if obj.modified_by is None:
            return None
        try:
            user = User.objects.get(id=obj.modified_by)
            return user.first_name
        except (User.DoesNotExist, ValueError):
            return None
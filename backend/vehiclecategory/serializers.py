from rest_framework import serializers
from vehiclecategory.models import VehicleCategory

class VehicleCategorySerializer(serializers.ModelSerializer):


    class Meta:
        model = VehicleCategory
        fields = ("id", "name", "active", "created_by", "created_at", "modified_by", "updated_at")
        #fields = '__all__'
        #fields = ('__all__')
from rest_framework import serializers
from vehicle.models import Vehicle
from dotenv import load_dotenv
import os
from django.contrib.auth.models import User

class VehicleSerializer(serializers.ModelSerializer):
    
    brand = serializers.CharField(source='vehiclemodel.brand.name')
    vehiclemodel = serializers.CharField(source='vehiclemodel.name')
    vehiclecategory = serializers.CharField(source='vehiclecategory.name')
    images = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d-%m-%Y") #13/12/2025
    modified_by_name = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(format="%d-%m-%Y") #13/12/2025

    class Meta:
        model = Vehicle
        fields = ("id",
                  "plate",
                  "brand",
                  "vehiclemodel",
                  "vehiclecategory",
                  "color",
                  "year",
                  "engine",
                  "engine_type",
                  "engine_number",
                  "vin",
                  "seat_count",
                  "description",
                  "status",
                  "images",
                  "active",
                  "created_by",
                  "created_by_name",
                  "created_at",
                  "modified_by",
                  "modified_by_name",
                  "updated_at"
                  )

    def get_images(self, obj):
        base = f"{os.getenv('BASE_URL')}:{os.getenv('BASE_URL_BACKEND_PORT')}/uploads/vehicle/"
        return [
            f"{base}{img.vehicle_image}"
            for img in obj.images.all()
        ]
    
    def get_created_by_name(self, obj):
        try:
            user = User.objects.get(id=obj.created_by)
            return user.first_name
        except User.DoesNotExist:
            return None
        except ValueError:
            return None
        
    def get_modified_by_name(self, obj):
        try:
            user = User.objects.get(id=obj.modified_by)
            return user.first_name
        except User.DoesNotExist:
            return None
        except ValueError:
            return None
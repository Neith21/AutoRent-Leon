from rest_framework import serializers
from vehiclemodel.models import VehicleModel
from django.contrib.auth.models import User

class VehicleModelSerializer(serializers.ModelSerializer):
    
    brand = serializers.CharField(source='brand.name')
    created_by_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d-%m-%Y") #13/12/2025
    modified_by_name = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(format="%d-%m-%Y") #13/12/2025

    class Meta:
        model = VehicleModel
        fields = ("id",
                  "name",
                  "brand_id",
                  "brand",
                  "active",
                  "created_by",
                  "created_by_name",
                  "created_at",
                  "modified_by",
                  "modified_by_name",
                  "updated_at"
                  )

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
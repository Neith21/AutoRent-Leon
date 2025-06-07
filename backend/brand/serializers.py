from rest_framework import serializers
from brand.models import Brand
from django.contrib.auth.models import User

class BrandSerializer(serializers.ModelSerializer):

    created_by_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d-%m-%Y") #13/12/2025
    modified_by_name = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(format="%d-%m-%Y") #13/12/2025

    class Meta:
        model = Brand
        fields = (
            "id",
            "name",
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

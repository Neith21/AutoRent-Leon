from rest_framework import serializers
from branch.models import Branch
from django.contrib.auth.models import User

class BranchSerializer(serializers.ModelSerializer):

    department = serializers.CharField(source='district.municipality.department.department')
    municipality = serializers.CharField(source='district.municipality.municipality')
    district = serializers.CharField(source='district.district')
    created_by_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d-%m-%Y") #13/12/2025
    modified_by_name = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(format="%d-%m-%Y") #13/12/2025


    class Meta:
        model = Branch
        fields = ("id",
                  "name",
                  "phone",
                  "address",
                  "department",
                  "municipality",
                  "district",
                  "email",
                  "active",
                  "created_by",
                  "created_by_name",
                  "created_at",
                  "modified_by",
                  "modified_by_name",
                  "updated_at")
        #fields = '__all__'
        #fields = ('__all__')


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
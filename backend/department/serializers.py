from rest_framework import serializers
from department.models import Department

class DepartmentSerializer(serializers.ModelSerializer):


    class Meta:
        model = Department
        fields = ("id", "code", "department", "active", "created_by", "created_at", "modified_by", "updated_at")
        #fields = '__all__'
        #fields = ('__all__')
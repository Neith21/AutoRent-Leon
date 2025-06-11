from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company

class CompanySerializer(serializers.ModelSerializer):

    created_by_name = serializers.SerializerMethodField()
    modified_by_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'trade_name', 'nrc', 'classification', 'phone', 
            'address', 'logo', 'logo_public_id', 'logo_lqip', 'email', 
            'website', 'active', 'created_by', 'created_by_name', 'created_at', 
            'modified_by', 'modified_by_name', 'updated_at'
        ]
        read_only_fields = [
            'logo', 'logo_public_id', 'logo_lqip', 'created_by', 'created_by_name', 
            'created_at', 'modified_by', 'modified_by_name', 'updated_at'
        ]

    def _get_user_name(self, user_id):
        if user_id is None:
            return None
        try:
            user = User.objects.get(id=user_id)
            return user.get_full_name() or user.username
        except User.DoesNotExist:
            return "Usuario Desconocido"

    def get_created_by_name(self, obj):
        return self._get_user_name(obj.created_by)

    def get_modified_by_name(self, obj):
        return self._get_user_name(obj.modified_by)
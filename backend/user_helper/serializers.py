from rest_framework import serializers
from user_control.models import UsersMetadata
from dotenv import load_dotenv
import os


def get_base_url():
        base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
        port = os.getenv("BASE_URL_BACKEND_PORT")
        if port:
            return f"{base_url}:{port}"
        return base_url


class UserHelperSerializer(serializers.ModelSerializer):
    
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = UsersMetadata
        fields = ("user_id", "username", "first_name", "last_name", "email", "user_image")

    def get_user_image(self, obj):
        base_url = get_base_url()
        return f"{base_url}/uploads/user/{obj.user_image}"
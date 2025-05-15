from rest_framework import serializers
from user_control.models import UsersMetadata
from dotenv import load_dotenv
import os

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
        return f"{os.getenv('BASE_URL')}:{os.getenv('BASE_URL_BACKEND_PORT')}/uploads/user/{obj.user_image}"
from rest_framework import serializers
from brand.models import Brand

class BrandSerializer(serializers.ModelSerializer):


    class Meta:
        model = Brand
        fields = ("id", "name", "active", "created_by", "created_at", "modified_by", "updated_at")
        #fields = '__all__'
        #fields = ('__all__')
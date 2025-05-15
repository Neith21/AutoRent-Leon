from rest_framework import serializers
from branch.models import Branch

class BranchSerializer(serializers.ModelSerializer):


    class Meta:
        model = Branch
        fields = ("id", "name", "phone", "address", "department", "district", "email")
        #fields = '__all__'
        #fields = ('__all__')
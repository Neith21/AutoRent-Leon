from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Invoice
from payment.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id',
            'amount',
            'payment_type',
            'payment_date',
            'concept',
            'reference'
        )

class InvoiceSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(source='rental.customer.__str__', read_only=True)
    customer_type = serializers.CharField(source='rental.customer.customer_type', read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    modified_by_name = serializers.SerializerMethodField(read_only=True)

    issue_date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            'id',
            'invoice_number',
            'rental_id',
            'customer_name',
            'customer_type',
            'issue_date',
            'total_amount',
            'reference',
            'status',
            'active',
            'created_by_name',
            'created_at',
            'modified_by_name',
            'updated_at',
        )

    def get_user_name(self, user_id):
        if user_id is None:
            return None
        try:
            user = User.objects.get(id=user_id)
            return user.get_full_name() or user.username
        except (User.DoesNotExist, ValueError):
            return "Usuario Desconocido"

    def get_created_by_name(self, obj):
        return self.get_user_name(obj.created_by)
    
    def get_modified_by_name(self, obj):
        return self.get_user_name(obj.modified_by)
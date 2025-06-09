# rental/serializers.py
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import decimal
from django.db.models import Sum

from .models import Payment, Invoice # Importa los modelos definidos en el mismo archivo
from django.contrib.auth.models import User


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'modified_by'] # Auditoría en el view

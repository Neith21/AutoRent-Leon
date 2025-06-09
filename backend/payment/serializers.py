# backend/payment/serializers.py

from rest_framework import serializers
from .models import Payment # Asegúrate de importar tu modelo Payment
# También podrías necesitar importar Rental si tu serializador de pago lo referencia
# from rental.models import Rental

class PaymentSerializer(serializers.ModelSerializer):
    # Campos personalizados o meta
    class Meta:
        model = Payment
        fields = '__all__' # O especifica los campos que necesites
        # Si necesitas campos de solo lectura o contexto del usuario
        # read_only_fields = ['created_at', 'updated_at', 'created_by', 'modified_by']

    # Si tienes algún método create o update personalizado en este serializador, asegúrate de que funcione
    # def create(self, validated_data):
    #     # Lógica para crear el pago
    #     return Payment.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     # Lógica para actualizar el pago
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance
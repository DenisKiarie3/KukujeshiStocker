from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order", "provider", "amount", "currency", "status", "paystack_reference", "verified_at", "created_at"]
        read_only_fields = fields  # all fields read-only via this endpoint — see views.py
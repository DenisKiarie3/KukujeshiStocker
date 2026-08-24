from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "variant", "quantity", "unit_price", "line_total"]
        read_only_fields = ["id", "unit_price", "line_total"]  # unit_price is set by the service, never by the client


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "store", "channel", "customer", "created_by",
            "status", "payment_status", "total", "items", "created_at",
        ]
        read_only_fields = ["id", "created_by", "status", "payment_status", "total", "created_at"]


class AddItemInputSerializer(serializers.Serializer):
    """
    Not a ModelSerializer — this validates the *input* to the add_item
    action, which isn't the same shape as an OrderItem (no order field;
    the order comes from the URL, and unit_price is derived, not supplied).
    """
    variant = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
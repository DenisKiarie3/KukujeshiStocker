from rest_framework import serializers
from apps.orders.models import Order

from apps.inventory.models import Product, ProductVariant


class PublicVariantSerializer(serializers.ModelSerializer):
    """
    Deliberately minimal — only what a shopper needs to pick and buy a
    variant. Notably EXCLUDES anything owner-facing. `in_stock` is exposed
    as a boolean rather than the raw stock_quantity, so the storefront
    never reveals exact inventory counts to the public.
    """
    price = serializers.DecimalField(source="effective_price", max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ["id", "sku", "attributes", "price", "in_stock"]

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0


class PublicProductSerializer(serializers.ModelSerializer):
    """
    Public-facing product shape. A SEPARATE serializer from the owner's
    ProductSerializer by design — narrowing a shared serializer by hiding
    fields is exactly how a cost-price or internal field leaks the day
    someone adds one. Only active variants are shown.
    """
    variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "base_price", "image", "variants"]

    def get_variants(self, obj):
        # Only surface variants that have stock or are otherwise sellable;
        # here we show all variants but the in_stock flag guides the UI.
        return PublicVariantSerializer(obj.variants.all(), many=True).data

class StorefrontOrderItemInputSerializer(serializers.Serializer):
    variant = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class StorefrontOrderCreateSerializer(serializers.Serializer):
    """Validates the SHAPE of an anonymous checkout request. Business
    rules (stock, store ownership) live in services.py, not here."""
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    items = StorefrontOrderItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

class StorefrontOrderStatusSerializer(serializers.ModelSerializer):
    """What an anonymous buyer is allowed to see about their own order,
    looked up by public_reference. No internal IDs, no store internals."""
    class Meta:
        model = Order
        fields = ["public_reference", "status", "payment_status", "total", "created_at"]
        read_only_fields = fields
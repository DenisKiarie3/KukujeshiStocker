from rest_framework import serializers

from .models import Category, Product, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "store", "name"]


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id", "product", "sku", "attributes", "price_override",
            "stock_quantity", "effective_price",
        ]
        read_only_fields = ["id", "stock_quantity"]  # never writable directly — see Phase 5 Step 1


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "store", "category", "name", "description",
            "base_price", "image", "is_active", "variants", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
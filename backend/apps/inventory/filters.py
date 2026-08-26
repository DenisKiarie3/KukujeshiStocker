import django_filters

from .models import Product, ProductVariant


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "is_active"]


class ProductVariantFilter(django_filters.FilterSet):
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = ProductVariant
        fields = ["sku"]

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(stock_quantity__gt=0) if value else queryset.filter(stock_quantity=0)
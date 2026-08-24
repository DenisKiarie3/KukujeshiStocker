from rest_framework import viewsets, permissions

from apps.core.models import Store
from .models import Category, Product, ProductVariant
from .serializers import CategorySerializer, ProductSerializer, ProductVariantSerializer


class StoreScopedMixin:
    """
    Shared by every inventory viewset: only ever returns objects belonging
    to stores the requesting user owns or staffs. Avoids repeating this
    filter logic three separate times below.
    """
    def get_user_stores(self):
        from django.db.models import Q
        return Store.objects.filter(
            Q(owner=self.request.user) | Q(staff__user=self.request.user)
        )


class CategoryViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(store__in=self.get_user_stores())


class ProductViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(store__in=self.get_user_stores())


class ProductVariantViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProductVariant.objects.filter(product__store__in=self.get_user_stores())
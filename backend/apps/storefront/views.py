from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from apps.core.models import Store
from apps.inventory.models import Product
from .serializers import PublicProductSerializer
from .throttles import StorefrontReadThrottle


class StorefrontProductListView(generics.ListAPIView):
    """
    Public, unauthenticated catalog for a single store, addressed by slug.
    Returns ONLY active products for that one store — never inactive
    products, never another store's data, never owner-facing fields.
    """
    serializer_class = PublicProductSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [StorefrontReadThrottle]

    def get_queryset(self):
        store = get_object_or_404(Store, slug=self.kwargs["slug"])
        return (
            Product.objects.filter(store=store, is_active=True)
            .prefetch_related("variants")
            .order_by("name")
        )
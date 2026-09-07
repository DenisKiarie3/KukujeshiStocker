from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.core.models import Store
from apps.inventory.models import Product
from .serializers import (
    PublicProductSerializer,
    StorefrontOrderCreateSerializer,
    StorefrontOrderStatusSerializer,
)
from .services import create_storefront_order, StorefrontError
from .throttles import StorefrontReadThrottle, StorefrontOrderThrottle


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

class StorefrontOrderCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [StorefrontOrderThrottle]

    def post(self, request, slug):
        store = get_object_or_404(Store, slug=slug)

        serializer = StorefrontOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = create_storefront_order(
                store=store,
                customer_data={"name": data["name"], "email": data["email"], "phone": data.get("phone", "")},
                items=data["items"],
            )
        except StorefrontError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Return the public_reference so the client can start checkout and
        # later poll status — never the internal integer id.
        return Response(
            {"public_reference": str(order.public_reference), "total": str(order.total)},
            status=status.HTTP_201_CREATED,
        )

class StorefrontOrderStatusView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [StorefrontReadThrottle]
    serializer_class = StorefrontOrderStatusSerializer
    lookup_field = "public_reference"
    queryset = Order.objects.all()
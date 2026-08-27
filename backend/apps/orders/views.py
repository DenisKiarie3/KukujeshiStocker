from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.core.models import Store
from apps.inventory.models import ProductVariant
from apps.inventory.services import InsufficientStockError
from apps.payments.models import Payment
from apps.payments.services import record_payment
from .models import Order
from .serializers import OrderSerializer, AddItemInputSerializer
from .services import add_item_to_order
from .filters import OrderFilter
from apps.payments.services import initiate_paystack_payment, PaymentNotAllowedError
from apps.payments.gateway import PaystackError


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = OrderFilter
    ordering_fields = ["created_at", "total"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user_stores = Store.objects.filter(
            Q(owner=self.request.user) | Q(staff__user=self.request.user)
        )
        return Order.objects.filter(store__in=user_stores)

    def perform_create(self, serializer):
        user_stores = Store.objects.filter(
            Q(owner=self.request.user) | Q(staff__user=self.request.user)
        )
        if serializer.validated_data["store"] not in user_stores:
            raise PermissionDenied("You do not have access to this store.")
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        # get_object() already applies get_queryset()'s store-scoping, so
        # requesting an order from a store you don't have access to 404s
        # here automatically — same pattern as Step 2's variant lookups.
        order = self.get_object()

        input_serializer = AddItemInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            variant = ProductVariant.objects.get(pk=input_serializer.validated_data["variant"])
        except ProductVariant.DoesNotExist:
            return Response({"detail": "Variant not found."}, status=status.HTTP_404_NOT_FOUND)

        # Defense in depth: even though the frontend should never send a
        # mismatched variant, the API itself must not trust that — a
        # variant from Store A must never be sellable on a Store B order.
        if variant.product.store_id != order.store_id:
            return Response(
                {"detail": "Variant does not belong to this order's store."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            add_item_to_order(order=order, variant=variant, quantity=input_serializer.validated_data["quantity"])
        except InsufficientStockError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        order.refresh_from_db()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="pay-cash")
    def pay_cash(self, request, pk=None):
        """
        Cash-only for now — this is what the POS "cash sale" button will
        call. Card/Paystack checkout is a different flow (Phase 7), since
        it needs an initiate → redirect → webhook-verify sequence instead
        of an instant confirm like cash.
        """
        order = self.get_object()
        record_payment(order=order, provider=Payment.Provider.CASH, amount=order.total)
        order.refresh_from_db()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="pay-online")
    def pay_online(self, request, pk=None):
        """
        Starts a Paystack checkout for this order. Returns the URL the
        frontend redirects the customer to. Does NOT mark anything paid —
        that only happens later, via the signature-verified webhook.
        """
        order = self.get_object()

        email = request.data.get("email")
        if not email:
            return Response({"detail": "Customer email is required for online payment."}, status=status.HTTP_400_BAD_REQUEST)

        if order.total <= 0:
            return Response({"detail": "Order has no payable total."}, status=status.HTTP_400_BAD_REQUEST)

        callback_url = f"{settings.FRONTEND_URL}/checkout/callback"
        try:
            checkout_url = initiate_paystack_payment(order=order, email=email, callback_url=callback_url)
        except PaymentNotAllowedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except PaystackError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"checkout_url": checkout_url}, status=status.HTTP_200_OK)
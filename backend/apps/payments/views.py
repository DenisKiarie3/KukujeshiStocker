from django.db.models import Q
from rest_framework import viewsets, permissions

from apps.core.models import Store
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only. The only sanctioned way to CREATE a payment is through
    record_payment() in services.py — right now that's reachable via
    Order.pay_cash; Paystack's webhook handler (Phase 7) will call it
    directly. There's no generic POST /payments/ endpoint on purpose.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_stores = Store.objects.filter(
            Q(owner=self.request.user) | Q(staff__user=self.request.user)
        )
        return Payment.objects.filter(order__store__in=user_stores)
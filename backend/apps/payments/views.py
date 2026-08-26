from django.db.models import Q
from rest_framework import viewsets, permissions

from apps.core.models import Store
from .models import Payment
from .serializers import PaymentSerializer
from .filters import PaymentFilter


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = PaymentFilter
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user_stores = Store.objects.filter(
            Q(owner=self.request.user) | Q(staff__user=self.request.user)
        )
        return Payment.objects.filter(order__store__in=user_stores)
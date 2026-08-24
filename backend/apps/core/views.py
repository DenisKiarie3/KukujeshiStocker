from rest_framework import viewsets, permissions
from django.db.models import Q

from .models import Store, StoreStaff
from .serializers import StoreSerializer, StoreStaffSerializer
from .permissions import IsStoreOwner


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated, IsStoreOwner]

    def get_queryset(self):
        # A user sees stores they own OR are staff at — never someone else's.
        user = self.request.user
        return Store.objects.filter(
            Q(owner=user) | Q(staff__user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class StoreStaffViewSet(viewsets.ModelViewSet):
    serializer_class = StoreStaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Scoped to stores the requesting user owns — you can't view or
        # edit staff lists for a store you don't own.
        return StoreStaff.objects.filter(store__owner=self.request.user)
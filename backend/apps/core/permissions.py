from rest_framework import permissions


class IsStoreOwner(permissions.BasePermission):
    """
    Object-level check: only the Store's owner can modify it. Read access
    for staff is handled separately in the queryset (see views.py) —
    this permission only governs write operations.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
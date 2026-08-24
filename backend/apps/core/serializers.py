from rest_framework import serializers

from .models import Store, StoreStaff


class StoreSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Store
        fields = ["id", "owner", "name", "slug", "currency", "address", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]


class StoreStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreStaff
        fields = ["id", "store", "user", "role", "added_at"]
        read_only_fields = ["id", "added_at"]
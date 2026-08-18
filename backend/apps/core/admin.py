from django.contrib import admin

from .models import Store, StoreStaff


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "slug", "currency", "created_at")
    search_fields = ("name", "slug")


@admin.register(StoreStaff)
class StoreStaffAdmin(admin.ModelAdmin):
    list_display = ("user", "store", "role", "added_at")
    list_filter = ("role",)
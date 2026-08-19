from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "amount", "currency", "status", "created_at")
    list_filter = ("provider", "status")
    readonly_fields = ("created_at", "verified_at")
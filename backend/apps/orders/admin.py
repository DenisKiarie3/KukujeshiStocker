from django.contrib import admin

from .models import Customer, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "email", "phone")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "store", "channel", "status", "payment_status", "total", "created_at")
    list_filter = ("channel", "status", "payment_status")
    readonly_fields = ("total",)
    inlines = [OrderItemInline]
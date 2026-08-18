from django.contrib import admin

from .models import Category, Product, ProductVariant, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "store")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    readonly_fields = ("stock_quantity",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "category", "base_price", "is_active")
    list_filter = ("store", "category", "is_active")
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "stock_quantity", "effective_price")
    readonly_fields = ("stock_quantity",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("variant", "movement_type", "quantity_change", "created_by", "created_at")
    list_filter = ("movement_type",)
    readonly_fields = ("created_at",)
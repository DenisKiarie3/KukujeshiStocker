from django.conf import settings
from django.db import models

from apps.core.models import Store


class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("store", "name")
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name} ({self.store})"


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    """
    A sellable unit of a Product — e.g. "Blue, Size M". Every Product has
    at least one variant, even one with no real variation, so the data
    model stays consistent either way.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=100, unique=True)
    attributes = models.JSONField(
        default=dict, blank=True, help_text='e.g. {"color": "blue", "size": "M"}'
    )
    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Leave blank to use the product's base_price.",
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Denormalized cache. Never edit directly — write a StockMovement instead; "
                   "services.py keeps this in sync transactionally.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} — {self.sku}"

    @property
    def effective_price(self):
        return self.price_override if self.price_override is not None else self.product.base_price


class StockMovement(models.Model):
    """
    Append-only ledger — the real source of truth for stock levels.
    ProductVariant.stock_quantity is just a cached sum of these, kept in
    sync by services.py (built in Phase 5). Never insert directly
    anywhere else.
    """
    class MovementType(models.TextChoices):
        PURCHASE = "purchase", "Purchase"
        SALE = "sale", "Sale"
        ADJUSTMENT = "adjustment", "Adjustment"
        RETURN = "return", "Return"

    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity_change = models.IntegerField(
        help_text="Positive = stock increase (purchase/return), negative = stock decrease (sale)."
    )
    reference = models.CharField(max_length=255, blank=True, help_text="e.g. order ID or supplier note")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="stock_movements"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.movement_type} {self.quantity_change:+d} — {self.variant.sku}"
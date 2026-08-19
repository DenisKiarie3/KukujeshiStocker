from django.conf import settings
from django.db import models

from apps.core.models import Store
from apps.inventory.models import ProductVariant


class Customer(models.Model):
    """
    A storefront customer. POS sales don't need one — walk-in buyers stay
    anonymous. Online orders can optionally link to a Customer, scoped to
    the store they bought from.
    """
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="customers")
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    class Channel(models.TextChoices):
        POS = "pos", "Point of Sale"
        ONLINE = "online", "Online Storefront"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="orders")
    channel = models.CharField(max_length=10, choices=Channel.choices)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders",
        help_text="Optional — POS walk-in sales usually leave this blank.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders_processed",
        help_text="Staff member who processed this sale (POS only; blank for online orders).",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        editable=False,
        help_text="Denormalized cache, summed from OrderItems. Synced in services.py — never edit directly.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} — {self.store} ({self.channel})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Snapshot of the variant's price at sale time — never re-derive from the "
                   "live variant price, since that can change after the order is placed.",
    )

    def __str__(self):
        return f"{self.quantity} x {self.variant.sku} (order #{self.order_id})"

    @property
    def line_total(self):
        return self.unit_price * self.quantity
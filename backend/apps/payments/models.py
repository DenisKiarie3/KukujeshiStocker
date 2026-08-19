from django.db import models

from apps.orders.models import Order


class Payment(models.Model):
    """
    A single payment attempt against an Order. Deliberately a ForeignKey,
    not a OneToOneField — a failed Paystack attempt followed by a retry
    means one Order can legitimately have more than one Payment row.
    """
    class Provider(models.TextChoices):
        CASH = "cash", "Cash"
        PAYSTACK = "paystack", "Paystack"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paystack_reference = models.CharField(max_length=255, blank=True, null=True, unique=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider} payment — {self.amount} {self.currency} ({self.status})"
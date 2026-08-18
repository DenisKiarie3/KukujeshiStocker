from django.conf import settings
from django.db import models


class Store(models.Model):
    """
    A single retailer's shop. Everything else in the app (products, staff,
    orders) is scoped to a Store, so this is the top-level tenant boundary.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_stores",
        help_text="The account that created and ultimately controls this store.",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="Used in the public storefront URL, e.g. /store/<slug>/")
    currency = models.CharField(max_length=3, default="KES")
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StoreStaff(models.Model):
    """
    Grants a user access to a store beyond ownership — e.g. a cashier who
    runs the POS, or a manager who can also edit inventory. The store's
    `owner` already has full access and doesn't need a row here; this
    table is for *additional* people.
    """
    class Role(models.TextChoices):
        MANAGER = "manager", "Manager"
        CASHIER = "cashier", "Cashier"

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="staff")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_roles")
    role = models.CharField(max_length=20, choices=Role.choices)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("store", "user")

    def __str__(self):
        return f"{self.user} — {self.role} at {self.store}"
from django.db import transaction

from apps.inventory.models import ProductVariant
from apps.orders.models import Order, OrderItem, Customer
from apps.orders.services import recalculate_order_total


class StorefrontError(Exception):
    """Raised for any business-rule violation during anonymous checkout."""


@transaction.atomic
def create_storefront_order(*, store, customer_data, items):
    """
    Creates an anonymous online order for `store`.

    Stock is VALIDATED (orders exceeding available stock are rejected) but
    deliberately NOT decremented here — that happens only when payment is
    confirmed via the Paystack webhook, per the storefront design decision.
    Prices are snapshotted server-side from each variant; nothing
    price-related is trusted from the caller. One transaction: any invalid
    line rolls back the whole order.
    """
    if not items:
        raise StorefrontError("Cannot create an empty order.")

    resolved = []
    for entry in items:
        variant_id = entry.get("variant")
        quantity = entry.get("quantity", 0)

        if not isinstance(quantity, int) or quantity < 1:
            raise StorefrontError(f"Invalid quantity for variant {variant_id}.")

        try:
            variant = ProductVariant.objects.select_related("product").get(pk=variant_id)
        except ProductVariant.DoesNotExist:
            raise StorefrontError(f"Variant {variant_id} does not exist.")

        if variant.product.store_id != store.id:
            raise StorefrontError(f"Variant {variant_id} does not belong to this store.")

        if not variant.product.is_active:
            raise StorefrontError(f"'{variant.product.name}' is not available for sale.")

        if variant.stock_quantity < quantity:
            raise StorefrontError(f"Not enough stock for '{variant.product.name}'.")

        resolved.append((variant, quantity))

    customer = Customer.objects.create(
        store=store,
        name=customer_data["name"],
        email=customer_data["email"],
        phone=customer_data.get("phone", ""),
    )

    order = Order.objects.create(
        store=store,
        channel=Order.Channel.ONLINE,
        customer=customer,
        created_by=None,
    )

    # Create line items with server-snapshotted prices, WITHOUT touching
    # the stock ledger — stock only moves on confirmed payment.
    for variant, quantity in resolved:
        OrderItem.objects.create(
            order=order,
            variant=variant,
            quantity=quantity,
            unit_price=variant.effective_price,
        )

    recalculate_order_total(order)
    order.refresh_from_db()
    return order
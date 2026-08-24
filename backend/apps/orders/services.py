from decimal import Decimal

from django.db import transaction

from apps.inventory.models import StockMovement
from apps.inventory.services import record_stock_movement
from .models import Order, OrderItem


@transaction.atomic
def add_item_to_order(*, order, variant, quantity, unit_price=None):
    """
    Adds a line item to an order, decrements stock through the inventory
    ledger, and recalculates the order's cached total — one transaction,
    so a stock shortage rolls back the whole operation instead of leaving
    an OrderItem that was never actually paid for in stock terms.
    """
    price = unit_price if unit_price is not None else variant.effective_price

    item = OrderItem.objects.create(
        order=order, variant=variant, quantity=quantity, unit_price=price
    )

    record_stock_movement(
        variant=variant,
        movement_type=StockMovement.MovementType.SALE,
        quantity_change=-quantity,
        reference=f"order #{order.pk}",
        created_by=order.created_by,
    )

    recalculate_order_total(order)
    return item


def recalculate_order_total(order):
    """
    Sums OrderItems fresh, rather than incrementing a running total.
    Unlike stock_quantity (which could accumulate thousands of movements
    over a variant's lifetime, where incremental updates matter for
    performance), an order's item list is small and bounded — a full
    recompute is cheap and immune to ever silently drifting from reality.
    """
    total = sum((item.line_total for item in order.items.all()), Decimal("0"))
    Order.objects.filter(pk=order.pk).update(total=total)
    order.refresh_from_db(fields=["total"])
    return order
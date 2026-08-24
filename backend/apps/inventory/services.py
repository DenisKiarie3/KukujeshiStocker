from django.db import transaction

from .models import ProductVariant, StockMovement


class InsufficientStockError(Exception):
    """Raised when a stock movement would take stock_quantity below zero."""


@transaction.atomic
def record_stock_movement(*, variant, movement_type, quantity_change, reference="", created_by=None):
    """
    The ONLY sanctioned way to change stock. Locks the variant row,
    validates the result won't go negative, writes an immutable
    StockMovement ledger entry, and updates the cached stock_quantity —
    all inside one atomic transaction.

    select_for_update() matters here: without it, two simultaneous sales
    of the last unit could both read stock_quantity=1, both decide it's
    safe to sell, and both succeed — leaving stock at -1. Locking the row
    for the duration of this transaction means the second sale has to
    wait for the first to finish, then sees the updated (now zero) count.
    """
    variant_locked = ProductVariant.objects.select_for_update().get(pk=variant.pk)

    resulting_quantity = variant_locked.stock_quantity + quantity_change
    if resulting_quantity < 0:
        raise InsufficientStockError(
            f"Cannot apply movement of {quantity_change} to {variant_locked.sku}: "
            f"would result in {resulting_quantity} (below zero)."
        )

    movement = StockMovement.objects.create(
        variant=variant_locked,
        movement_type=movement_type,
        quantity_change=quantity_change,
        reference=reference,
        created_by=created_by,
    )
    variant_locked.stock_quantity = resulting_quantity
    variant_locked.save(update_fields=["stock_quantity"])
    return movement
import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Payment
from . import gateway
from apps.orders.models import Order
from apps.inventory.services import record_stock_movement, InsufficientStockError
from apps.inventory.models import StockMovement


@transaction.atomic
def record_payment(*, order, provider, amount, currency="KES", paystack_reference=None, status=Payment.Status.SUCCESS):
    """
    The one sanctioned way to record a payment. Cash-at-POS calls this
    directly; the Paystack webhook calls it once a transaction is verified.
    """
    payment = Payment.objects.create(
        order=order,
        provider=provider,
        amount=amount,
        currency=currency,
        status=status,
        paystack_reference=paystack_reference,
    )
    if status == Payment.Status.SUCCESS:
        Order.objects.filter(pk=order.pk).update(payment_status=Order.PaymentStatus.PAID)
        order.refresh_from_db(fields=["payment_status"])
    return payment

class PaymentNotAllowedError(Exception):
    """Raised when an order cannot accept a new payment attempt."""

def initiate_paystack_payment(*, order, email, callback_url):
    if order.payment_status == Order.PaymentStatus.PAID:
        raise PaymentNotAllowedError("This order has already been paid.")
    if order.status == Order.Status.CANCELLED:
        raise PaymentNotAllowedError("Cannot pay for a cancelled order.")

    reference = f"kjs-{order.pk}-{uuid.uuid4().hex[:12]}"
    amount_kobo = int(order.total * 100)

    result = gateway.initialize_transaction(
        email=email,
        amount_kobo=amount_kobo,
        reference=reference,
        callback_url=callback_url,
        currency=order.store.currency,
    )

    Payment.objects.create(
        order=order,
        provider=Payment.Provider.PAYSTACK,
        amount=order.total,
        currency=order.store.currency,
        status=Payment.Status.PENDING,
        paystack_reference=reference,
    )
    return result["authorization_url"]


@transaction.atomic
def confirm_paystack_payment(*, reference):
    """
    Called by the webhook handler AFTER signature verification. Independently
    verifies with Paystack, checks the amount, is idempotent, and — on the
    genuine first confirmation only — decrements stock for the order's items.

    The stock decrement sits AFTER the idempotency guard, so a replayed
    webhook (which does happen) never double-decrements: a replay hits the
    early return before reaching this code.
    """
    try:
        payment = Payment.objects.select_for_update().get(
            paystack_reference=reference, provider=Payment.Provider.PAYSTACK
        )
    except Payment.DoesNotExist:
        return None

    # Idempotency guard — a replayed webhook for an already-successful
    # payment stops here, before any stock movement.
    if payment.status == Payment.Status.SUCCESS:
        return payment

    verified = gateway.verify_transaction(reference=reference)

    paystack_amount = Decimal(verified["amount"]) / 100
    if verified.get("status") != "success" or paystack_amount != payment.amount:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        return payment

    # Genuine first-time confirmation. Decrement stock for each line item
    # now — this is the point of sale for an online order. If stock ran out
    # between order creation and payment (we validate but don't reserve),
    # the payment still succeeds (the customer paid) but the order is
    # flagged for manual resolution rather than silently over-selling.
    order = payment.order
    stock_ok = True
    for item in order.items.select_related("variant").all():
        try:
            record_stock_movement(
                variant=item.variant,
                movement_type=StockMovement.MovementType.SALE,
                quantity_change=-item.quantity,
                reference=f"online order {order.public_reference}",
            )
        except InsufficientStockError:
            stock_ok = False

    payment.status = Payment.Status.SUCCESS
    payment.verified_at = timezone.now()
    payment.save(update_fields=["status", "verified_at"])

    Order.objects.filter(pk=order.pk).update(
        payment_status=Order.PaymentStatus.PAID,
        status=Order.Status.COMPLETED if stock_ok else Order.Status.NEEDS_ATTENTION,
    )
    return payment
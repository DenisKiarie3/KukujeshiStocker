import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Payment
from . import gateway
from apps.orders.models import Order


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


def initiate_paystack_payment(*, order, email, callback_url):
    """
    Starts a Paystack transaction for an order and returns the checkout URL
    the frontend should redirect the customer to. Generates a unique
    reference we control (rather than letting Paystack generate one), so we
    can correlate the later webhook back to this exact order.
    """
    reference = f"kjs-{order.pk}-{uuid.uuid4().hex[:12]}"
    amount_kobo = int(order.total * 100)  # KES -> kobo; Decimal * 100 then int

    result = gateway.initialize_transaction(
        email=email,
        amount_kobo=amount_kobo,
        reference=reference,
        callback_url=callback_url,
        currency=order.store.currency,
    )

    # Record a PENDING payment now, so a webhook that arrives before any
    # other bookkeeping has a row to find and flip. The reference is the
    # correlation key between this row and the eventual webhook.
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
    Called by the webhook handler AFTER the signature has been verified.
    Independently confirms with Paystack's verify endpoint, checks the
    amount, and is idempotent — a replayed webhook for an
    already-successful payment is a no-op, not a double-fulfillment.
    """
    try:
        payment = Payment.objects.select_for_update().get(
            paystack_reference=reference, provider=Payment.Provider.PAYSTACK
        )
    except Payment.DoesNotExist:
        # A reference we never issued — ignore rather than create anything.
        return None

    # Idempotency: if we already marked this successful, stop here.
    if payment.status == Payment.Status.SUCCESS:
        return payment

    verified = gateway.verify_transaction(reference=reference)

    # Independent amount check — never trust the webhook's self-report.
    paystack_amount = Decimal(verified["amount"]) / 100
    if verified.get("status") != "success" or paystack_amount != payment.amount:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        return payment

    payment.status = Payment.Status.SUCCESS
    payment.verified_at = timezone.now()
    payment.save(update_fields=["status", "verified_at"])

    Order.objects.filter(pk=payment.order_id).update(payment_status=Order.PaymentStatus.PAID)
    return payment
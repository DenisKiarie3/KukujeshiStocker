from django.db import transaction

from .models import Payment
from apps.orders.models import Order


@transaction.atomic
def record_payment(*, order, provider, amount, currency="KES", paystack_reference=None, status=Payment.Status.SUCCESS):
    """
    The one sanctioned way to record a payment. For now this only handles
    the cash-at-POS case directly — the Paystack flow (Phase 7) will call
    this same function from a webhook handler once a transaction is
    verified, rather than duplicating the "mark order paid" logic here.
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
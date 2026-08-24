from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.models import Store
from apps.orders.models import Order
from .models import Payment

from .services import record_payment

User = get_user_model()


class PaymentModelTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="owner4", email="owner4@example.com", password="x")
        self.store = Store.objects.create(owner=owner, name="Shop D", slug="shop-d")
        self.order = Order.objects.create(store=self.store, channel=Order.Channel.ONLINE)

    def test_create_pending_paystack_payment(self):
        payment = Payment.objects.create(
            order=self.order, provider=Payment.Provider.PAYSTACK, amount=Decimal("100.00")
        )
        self.assertEqual(payment.status, Payment.Status.PENDING)

    def test_order_can_have_multiple_payment_attempts(self):
        Payment.objects.create(
            order=self.order, provider=Payment.Provider.PAYSTACK, amount=Decimal("100.00"),
            status=Payment.Status.FAILED,
        )
        Payment.objects.create(
            order=self.order, provider=Payment.Provider.PAYSTACK, amount=Decimal("100.00"),
            status=Payment.Status.SUCCESS,
        )
        self.assertEqual(self.order.payments.count(), 2)

class PaymentServiceTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="payservice1", email="payservice1@example.com", password="x")
        store = Store.objects.create(owner=owner, name="Shop G", slug="shop-g")
        self.order = Order.objects.create(store=store, channel=Order.Channel.POS, total=Decimal("200.00"))

    def test_successful_payment_marks_order_paid(self):
        record_payment(order=self.order, provider=Payment.Provider.CASH, amount=Decimal("200.00"))
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)
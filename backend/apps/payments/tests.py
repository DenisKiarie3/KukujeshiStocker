from decimal import Decimal

import json
import hashlib
import hmac
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import override_settings

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

class PaystackServiceTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="pssvc1", email="pssvc1@example.com", password="x")
        store = Store.objects.create(owner=owner, name="PS Shop", slug="ps-shop")
        self.order = Order.objects.create(store=store, channel=Order.Channel.ONLINE, total=Decimal("250.00"))

    @patch("apps.payments.services.gateway.initialize_transaction")
    def test_initiate_creates_pending_payment_and_returns_url(self, mock_init):
        mock_init.return_value = {"authorization_url": "https://checkout.paystack.co/xyz", "reference": "kjs-x"}
        url = __import__("apps.payments.services", fromlist=["initiate_paystack_payment"]).initiate_paystack_payment(
            order=self.order, email="buyer@example.com", callback_url="http://localhost:5173/checkout/callback"
        )
        self.assertEqual(url, "https://checkout.paystack.co/xyz")
        payment = self.order.payments.get()
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.provider, Payment.Provider.PAYSTACK)

    @patch("apps.payments.services.gateway.verify_transaction")
    def test_confirm_marks_paid_when_amount_matches(self, mock_verify):
        from apps.payments.services import confirm_paystack_payment
        Payment.objects.create(
            order=self.order, provider=Payment.Provider.PAYSTACK, amount=Decimal("250.00"),
            status=Payment.Status.PENDING, paystack_reference="kjs-ref-1",
        )
        mock_verify.return_value = {"status": "success", "amount": 25000, "reference": "kjs-ref-1"}

        payment = confirm_paystack_payment(reference="kjs-ref-1")
        self.order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.SUCCESS)
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)

    @patch("apps.payments.services.gateway.verify_transaction")
    def test_confirm_fails_on_amount_mismatch(self, mock_verify):
        from apps.payments.services import confirm_paystack_payment
        Payment.objects.create(
            order=self.order, provider=Payment.Provider.PAYSTACK, amount=Decimal("250.00"),
            status=Payment.Status.PENDING, paystack_reference="kjs-ref-2",
        )
        # Paystack reports a DIFFERENT (smaller) amount than the order total.
        mock_verify.return_value = {"status": "success", "amount": 500, "reference": "kjs-ref-2"}

        payment = confirm_paystack_payment(reference="kjs-ref-2")
        self.order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.FAILED)
        self.assertNotEqual(self.order.payment_status, Order.PaymentStatus.PAID)

    @patch("apps.payments.services.gateway.verify_transaction")
    def test_confirm_is_idempotent_on_already_successful(self, mock_verify):
        from apps.payments.services import confirm_paystack_payment
        Payment.objects.create(
            order=self.order, provider=Payment.Provider.PAYSTACK, amount=Decimal("250.00"),
            status=Payment.Status.SUCCESS, paystack_reference="kjs-ref-3",
        )
        confirm_paystack_payment(reference="kjs-ref-3")
        mock_verify.assert_not_called()  # short-circuited before ever calling Paystack again

    def test_confirm_ignores_unknown_reference(self):
        from apps.payments.services import confirm_paystack_payment
        result = confirm_paystack_payment(reference="reference-we-never-issued")
        self.assertIsNone(result)


@override_settings(PAYSTACK_SECRET_KEY="sk_test_dummy_secret")
class PaystackWebhookTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="pswh1", email="pswh1@example.com", password="x")
        store = Store.objects.create(owner=owner, name="WH Shop", slug="wh-shop")
        self.order = Order.objects.create(store=store, channel=Order.Channel.ONLINE, total=Decimal("250.00"))
        Payment.objects.create(
            order=self.order, provider=Payment.Provider.PAYSTACK, amount=Decimal("250.00"),
            status=Payment.Status.PENDING, paystack_reference="kjs-wh-1",
        )

    def _signed_post(self, body_dict):
        body = json.dumps(body_dict).encode("utf-8")
        signature = hmac.new(b"sk_test_dummy_secret", body, hashlib.sha512).hexdigest()
        return self.client.post(
            "/api/v1/webhooks/paystack/", data=body, content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE=signature,
        )

    def test_webhook_rejects_missing_signature(self):
        response = self.client.post(
            "/api/v1/webhooks/paystack/", data=json.dumps({"event": "charge.success"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_webhook_rejects_bad_signature(self):
        response = self.client.post(
            "/api/v1/webhooks/paystack/", data=json.dumps({"event": "charge.success"}),
            content_type="application/json", HTTP_X_PAYSTACK_SIGNATURE="wrong",
        )
        self.assertEqual(response.status_code, 403)

    @patch("apps.payments.services.gateway.verify_transaction")
    def test_valid_webhook_confirms_payment(self, mock_verify):
        mock_verify.return_value = {"status": "success", "amount": 25000, "reference": "kjs-wh-1"}
        response = self._signed_post({"event": "charge.success", "data": {"reference": "kjs-wh-1"}})
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)

    def test_valid_but_unhandled_event_returns_200(self):
        response = self._signed_post({"event": "charge.failed", "data": {"reference": "kjs-wh-1"}})
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertNotEqual(self.order.payment_status, Order.PaymentStatus.PAID)
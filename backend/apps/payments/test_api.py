from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from apps.core.models import Store
from apps.orders.models import Order
from .models import Payment

User = get_user_model()


class PaymentAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="payowner1", email="payowner1@example.com", password="x")
        self.other_user = User.objects.create_user(username="payowner2", email="payowner2@example.com", password="x")
        self.store = Store.objects.create(owner=self.owner, name="Pay Shop", slug="pay-shop")
        self.order = Order.objects.create(store=self.store, channel=Order.Channel.POS)
        Payment.objects.create(order=self.order, provider=Payment.Provider.CASH, amount=Decimal("500.00"))

    def test_owner_can_list_their_store_payments(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/v1/payments/")
        self.assertEqual(len(response.data["results"]), 1)

    def test_other_user_cannot_see_this_payment(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get("/api/v1/payments/")
        self.assertEqual(len(response.data["results"]), 0)

    def test_direct_post_to_payments_is_not_allowed(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post("/api/v1/payments/", {"order": self.order.pk, "provider": "cash", "amount": "100.00"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

class PaymentFilterTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="payfilter1", email="payfilter1@example.com", password="x")
        self.store = Store.objects.create(owner=self.owner, name="Pay Filter Shop", slug="pay-filter-shop")
        order = Order.objects.create(store=self.store, channel=Order.Channel.POS)
        Payment.objects.create(order=order, provider=Payment.Provider.CASH, amount=Decimal("100.00"), status=Payment.Status.SUCCESS)
        Payment.objects.create(order=order, provider=Payment.Provider.PAYSTACK, amount=Decimal("200.00"), status=Payment.Status.FAILED)
        self.client.force_authenticate(user=self.owner)

    def test_filter_payments_by_provider(self):
        response = self.client.get("/api/v1/payments/?provider=paystack")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["provider"], "paystack")

    def test_filter_payments_by_status(self):
        response = self.client.get("/api/v1/payments/?status=failed")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
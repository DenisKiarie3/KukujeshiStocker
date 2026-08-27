from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from apps.core.models import Store
from apps.inventory.models import Product, ProductVariant
from apps.inventory.services import record_stock_movement
from apps.inventory.models import StockMovement
from .models import Order

User = get_user_model()


class OrderAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="orderowner1", email="orderowner1@example.com", password="x")
        self.store = Store.objects.create(owner=self.owner, name="Order Shop", slug="order-shop")
        other_store_owner = User.objects.create_user(username="otherowner", email="otherowner@example.com", password="x")
        self.other_store = Store.objects.create(owner=other_store_owner, name="Other Shop", slug="other-shop")

        product = Product.objects.create(store=self.store, name="Cooking Oil 1L", base_price=Decimal("300.00"))
        self.variant = ProductVariant.objects.create(product=product, sku="OIL-1L")
        record_stock_movement(variant=self.variant, movement_type=StockMovement.MovementType.PURCHASE, quantity_change=10)

        self.client.force_authenticate(user=self.owner)
        self.order = Order.objects.create(store=self.store, channel=Order.Channel.POS, created_by=self.owner)

    def test_add_item_success(self):
        response = self.client.post(
            f"/api/v1/orders/{self.order.pk}/add_item/", {"variant": self.variant.pk, "quantity": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data["total"]), Decimal("600.00"))

    def test_add_item_insufficient_stock_returns_400(self):
        response = self.client.post(
            f"/api/v1/orders/{self.order.pk}/add_item/", {"variant": self.variant.pk, "quantity": 999}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_order_for_store_you_do_not_own(self):
        response = self.client.post(
            "/api/v1/orders/", {"store": self.other_store.pk, "channel": Order.Channel.POS}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pay_cash_marks_order_paid(self):
        self.client.post(f"/api/v1/orders/{self.order.pk}/add_item/", {"variant": self.variant.pk, "quantity": 1})
        response = self.client.post(f"/api/v1/orders/{self.order.pk}/pay-cash/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_status"], Order.PaymentStatus.PAID)

    @patch("apps.orders.views.initiate_paystack_payment")
    def test_pay_online_returns_checkout_url(self, mock_initiate):
        self.client.post(f"/api/v1/orders/{self.order.pk}/add_item/", {"variant": self.variant.pk, "quantity": 1})
        mock_initiate.return_value = "https://checkout.paystack.co/redirect-here"
        response = self.client.post(
            f"/api/v1/orders/{self.order.pk}/pay-online/", {"email": "buyer@example.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["checkout_url"], "https://checkout.paystack.co/redirect-here")

    def test_pay_online_requires_email(self):
        self.client.post(f"/api/v1/orders/{self.order.pk}/add_item/", {"variant": self.variant.pk, "quantity": 1})
        response = self.client.post(f"/api/v1/orders/{self.order.pk}/pay-online/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_pay_online_for_already_paid_order(self):
        self.client.post(f"/api/v1/orders/{self.order.pk}/add_item/", {"variant": self.variant.pk, "quantity": 1})
        self.order.payment_status = Order.PaymentStatus.PAID
        self.order.save(update_fields=["payment_status"])
        response = self.client.post(f"/api/v1/orders/{self.order.pk}/pay-online/", {"email": "buyer@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_pay_online_for_cancelled_order(self):
        self.client.post(f"/api/v1/orders/{self.order.pk}/add_item/", {"variant": self.variant.pk, "quantity": 1})
        self.order.status = Order.Status.CANCELLED
        self.order.save(update_fields=["status"])
        response = self.client.post(f"/api/v1/orders/{self.order.pk}/pay-online/", {"email": "buyer@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class OrderFilterTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="orderfilter1", email="orderfilter1@example.com", password="x")
        self.store = Store.objects.create(owner=self.owner, name="Order Filter Shop", slug="order-filter-shop")
        Order.objects.create(store=self.store, channel=Order.Channel.POS, status=Order.Status.COMPLETED)
        Order.objects.create(store=self.store, channel=Order.Channel.ONLINE, status=Order.Status.PENDING)
        self.client.force_authenticate(user=self.owner)

    def test_filter_orders_by_channel(self):
        response = self.client.get("/api/v1/orders/?channel=online")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["channel"], "online")

    def test_filter_orders_by_status(self):
        response = self.client.get("/api/v1/orders/?status=completed")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
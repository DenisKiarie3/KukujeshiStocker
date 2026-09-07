from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from apps.core.models import Store
from apps.inventory.models import Product, ProductVariant, StockMovement
from apps.inventory.services import record_stock_movement
from apps.orders.models import Order
from unittest.mock import patch

User = get_user_model()


class StorefrontProductEndpointTests(APITestCase):
    def setUp(self):
        owner = User.objects.create_user(username="sfowner1", email="sfowner1@example.com", password="x")
        self.store = Store.objects.create(owner=owner, name="Corner Shop", slug="corner-shop")
        self.active = Product.objects.create(store=self.store, name="Bread", base_price=Decimal("60.00"), is_active=True)
        ProductVariant.objects.create(product=self.active, sku="BREAD-1")
        self.inactive = Product.objects.create(store=self.store, name="Discontinued", base_price=Decimal("10.00"), is_active=False)

        # A second store, whose products must never appear under corner-shop's slug.
        other_owner = User.objects.create_user(username="sfowner2", email="sfowner2@example.com", password="x")
        self.other_store = Store.objects.create(owner=other_owner, name="Other Shop", slug="other-shop")
        Product.objects.create(store=self.other_store, name="Not Mine", base_price=Decimal("99.00"), is_active=True)

    def test_public_endpoint_needs_no_auth(self):
        response = self.client.get("/api/v1/storefront/corner-shop/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_active_products_returned(self):
        response = self.client.get("/api/v1/storefront/corner-shop/products/")
        names = [p["name"] for p in response.data["results"]]
        self.assertIn("Bread", names)
        self.assertNotIn("Discontinued", names)

    def test_other_stores_products_not_leaked(self):
        response = self.client.get("/api/v1/storefront/corner-shop/products/")
        names = [p["name"] for p in response.data["results"]]
        self.assertNotIn("Not Mine", names)

    def test_public_serializer_hides_owner_fields(self):
        response = self.client.get("/api/v1/storefront/corner-shop/products/")
        product = response.data["results"][0]
        # is_active and created_at are owner-facing — must not appear publicly.
        self.assertNotIn("is_active", product)
        self.assertNotIn("created_at", product)
        # Variants expose a boolean, never the raw count.
        self.assertIn("in_stock", product["variants"][0])
        self.assertNotIn("stock_quantity", product["variants"][0])

    def test_unknown_slug_returns_404(self):
        response = self.client.get("/api/v1/storefront/no-such-store/products/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class StorefrontOrderCreationTests(APITestCase):
    def setUp(self):
        owner = User.objects.create_user(username="sforder1", email="sforder1@example.com", password="x")
        self.store = Store.objects.create(owner=owner, name="Order Store", slug="order-store")
        product = Product.objects.create(store=self.store, name="Maize Flour", base_price=Decimal("150.00"), is_active=True)
        self.variant = ProductVariant.objects.create(product=product, sku="FLOUR-2KG")
        record_stock_movement(variant=self.variant, movement_type=StockMovement.MovementType.PURCHASE, quantity_change=10)

        other_owner = User.objects.create_user(username="sforder2", email="sforder2@example.com", password="x")
        self.other_store = Store.objects.create(owner=other_owner, name="Other", slug="other-order-store")
        other_product = Product.objects.create(store=self.other_store, name="Rice", base_price=Decimal("200.00"), is_active=True)
        self.other_variant = ProductVariant.objects.create(product=other_product, sku="RICE-X")
        record_stock_movement(variant=self.other_variant, movement_type=StockMovement.MovementType.PURCHASE, quantity_change=10)

    def _payload(self, **overrides):
        payload = {
            "name": "Jane Buyer", "email": "jane@example.com", "phone": "0712345678",
            "items": [{"variant": self.variant.pk, "quantity": 2}],
        }
        payload.update(overrides)
        return payload

    def test_anonymous_can_create_order(self):
        response = self.client.post("/api/v1/storefront/order-store/orders/", self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("public_reference", response.data)
        self.assertEqual(response.data["total"], "300.00")  # 2 x 150

    def test_order_does_not_decrement_stock_at_creation(self):
        self.client.post("/api/v1/storefront/order-store/orders/", self._payload(), format="json")
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 10)  # unchanged until payment

    def test_created_order_is_anonymous_and_pending(self):
        response = self.client.post("/api/v1/storefront/order-store/orders/", self._payload(), format="json")
        order = Order.objects.get(public_reference=response.data["public_reference"])
        self.assertIsNone(order.created_by)
        self.assertEqual(order.payment_status, Order.PaymentStatus.PENDING)
        self.assertEqual(order.channel, Order.Channel.ONLINE)

    def test_cannot_buy_variant_from_another_store(self):
        response = self.client.post(
            "/api/v1/storefront/order-store/orders/",
            self._payload(items=[{"variant": self.other_variant.pk, "quantity": 1}]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_order_more_than_available_stock(self):
        response = self.client.post(
            "/api/v1/storefront/order-store/orders/",
            self._payload(items=[{"variant": self.variant.pk, "quantity": 999}]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_items_rejected(self):
        response = self.client.post("/api/v1/storefront/order-store/orders/", self._payload(items=[]), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_rejected(self):
        response = self.client.post(
            "/api/v1/storefront/order-store/orders/", self._payload(email="not-an-email"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.storefront.views.initiate_paystack_payment")
    def test_checkout_returns_paystack_url(self, mock_initiate):
        create_resp = self.client.post("/api/v1/storefront/order-store/orders/", self._payload(), format="json")
        ref = create_resp.data["public_reference"]
        mock_initiate.return_value = "https://checkout.paystack.co/storefront-xyz"
        response = self.client.post(f"/api/v1/storefront/orders/{ref}/checkout/", {"email": "jane@example.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["checkout_url"], "https://checkout.paystack.co/storefront-xyz")
        # The callback_url must carry the order reference, or the frontend
        # callback page has no way to know which order to poll.
        _, kwargs = mock_initiate.call_args
        self.assertIn(f"order={ref}", kwargs["callback_url"])

class StorefrontOrderStatusTests(APITestCase):
    def setUp(self):
        owner = User.objects.create_user(username="sfstatus1", email="sfstatus1@example.com", password="x")
        self.store = Store.objects.create(owner=owner, name="Status Store", slug="status-store")
        self.order = Order.objects.create(store=self.store, channel=Order.Channel.ONLINE, total=Decimal("500.00"))

    def test_status_lookup_by_public_reference(self):
        response = self.client.get(f"/api/v1/storefront/orders/{self.order.public_reference}/status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["payment_status"], "pending")

    def test_status_lookup_exposes_only_safe_fields(self):
        response = self.client.get(f"/api/v1/storefront/orders/{self.order.public_reference}/status/")
        self.assertNotIn("store", response.data)
        self.assertNotIn("id", response.data)
        self.assertNotIn("customer", response.data)

    def test_unknown_reference_returns_404(self):
        import uuid
        response = self.client.get(f"/api/v1/storefront/orders/{uuid.uuid4()}/status/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
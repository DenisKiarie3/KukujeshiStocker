from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from apps.core.models import Store
from apps.inventory.models import Product, ProductVariant

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
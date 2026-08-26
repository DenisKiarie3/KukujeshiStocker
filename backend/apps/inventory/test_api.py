from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from apps.core.models import Store
from .models import Category, Product, ProductVariant  # Category added

User = get_user_model()


class ProductAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="apiowner3", email="apiowner3@example.com", password="x")
        self.other_user = User.objects.create_user(username="apiowner4", email="apiowner4@example.com", password="x")
        self.store = Store.objects.create(owner=self.owner, name="Inv Shop", slug="inv-shop")
        self.product = Product.objects.create(store=self.store, name="Eggs (tray)", base_price=Decimal("400.00"))
        self.variant = ProductVariant.objects.create(product=self.product, sku="EGGS-TRAY")

    def test_stock_quantity_is_not_writable_via_api(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f"/api/v1/variants/{self.variant.pk}/", {"stock_quantity": 9999}, format="json"
        )
        self.variant.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.variant.stock_quantity, 0)  # unchanged, despite the request trying to set it

    def test_product_includes_nested_variants(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f"/api/v1/products/{self.product.pk}/")
        self.assertEqual(len(response.data["variants"]), 1)
        self.assertEqual(response.data["variants"][0]["sku"], "EGGS-TRAY")

    def test_other_user_cannot_access_this_products_variants(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f"/api/v1/variants/{self.variant.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ProductFilterAndPaginationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="filterowner1", email="filterowner1@example.com", password="x")
        self.store = Store.objects.create(owner=self.owner, name="Filter Shop", slug="filter-shop")
        self.category_a = Category.objects.create(store=self.store, name="Drinks")
        self.category_b = Category.objects.create(store=self.store, name="Snacks")
        Product.objects.create(store=self.store, category=self.category_a, name="Cola", base_price=Decimal("80.00"))
        Product.objects.create(store=self.store, category=self.category_b, name="Chips", base_price=Decimal("150.00"))
        self.client.force_authenticate(user=self.owner)

    def test_filter_products_by_category(self):
        response = self.client.get(f"/api/v1/products/?category={self.category_a.pk}")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Cola")

    def test_filter_products_by_price_range(self):
        response = self.client.get("/api/v1/products/?min_price=100")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Chips")

    def test_order_products_by_price_descending(self):
        response = self.client.get("/api/v1/products/?ordering=-base_price")
        results = response.data["results"]
        self.assertEqual(results[0]["name"], "Chips")

    def test_pagination_returns_paginated_shape(self):
        response = self.client.get("/api/v1/products/")
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
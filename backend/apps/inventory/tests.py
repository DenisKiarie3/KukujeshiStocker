from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.models import Store
from .models import Category, Product, ProductVariant, StockMovement

from .services import record_stock_movement, InsufficientStockError

User = get_user_model()


class InventoryModelTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="owner2", email="owner2@example.com", password="x")
        self.store = Store.objects.create(owner=owner, name="Shop B", slug="shop-b")
        self.category = Category.objects.create(store=self.store, name="Beverages")
        self.product = Product.objects.create(
            store=self.store, category=self.category, name="Soda", base_price=Decimal("50.00")
        )

    def test_variant_falls_back_to_base_price(self):
        variant = ProductVariant.objects.create(product=self.product, sku="SODA-500ML")
        self.assertEqual(variant.effective_price, Decimal("50.00"))

    def test_variant_price_override(self):
        variant = ProductVariant.objects.create(
            product=self.product, sku="SODA-1L", price_override=Decimal("90.00")
        )
        self.assertEqual(variant.effective_price, Decimal("90.00"))

    def test_stock_movement_does_not_auto_update_cache_yet(self):
        # services.py (Phase 5) will wire this up. For now, confirm the
        # ledger entry saves correctly and the cache is untouched.
        variant = ProductVariant.objects.create(product=self.product, sku="SODA-CRATE")
        StockMovement.objects.create(variant=variant, movement_type=StockMovement.MovementType.PURCHASE, quantity_change=24)
        variant.refresh_from_db()
        self.assertEqual(variant.stock_quantity, 0)

class StockMovementServiceTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="owner5", email="owner5@example.com", password="x")
        store = Store.objects.create(owner=owner, name="Shop E", slug="shop-e")
        product = Product.objects.create(store=store, name="Rice 2kg", base_price=Decimal("250.00"))
        self.variant = ProductVariant.objects.create(product=product, sku="RICE-2KG")

    def test_purchase_increases_stock(self):
        record_stock_movement(
            variant=self.variant, movement_type=StockMovement.MovementType.PURCHASE, quantity_change=50
        )
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 50)

    def test_sale_decreases_stock(self):
        record_stock_movement(
            variant=self.variant, movement_type=StockMovement.MovementType.PURCHASE, quantity_change=50
        )
        record_stock_movement(
            variant=self.variant, movement_type=StockMovement.MovementType.SALE, quantity_change=-10
        )
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 40)

    def test_sale_exceeding_stock_raises_and_does_not_create_movement(self):
        record_stock_movement(
            variant=self.variant, movement_type=StockMovement.MovementType.PURCHASE, quantity_change=5
        )
        with self.assertRaises(InsufficientStockError):
            record_stock_movement(
                variant=self.variant, movement_type=StockMovement.MovementType.SALE, quantity_change=-10
            )
        self.variant.refresh_from_db()
        # Confirms the whole transaction rolled back — stock is still 5,
        # and no bad StockMovement row was left behind.
        self.assertEqual(self.variant.stock_quantity, 5)
        self.assertEqual(self.variant.movements.count(), 1)
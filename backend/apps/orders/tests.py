from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.models import Store
from apps.inventory.models import Product, ProductVariant
from .models import Customer, Order, OrderItem

from .services import add_item_to_order
from apps.inventory.services import InsufficientStockError

User = get_user_model()


class OrderModelTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="owner3", email="owner3@example.com", password="x")
        self.store = Store.objects.create(owner=owner, name="Shop C", slug="shop-c")
        product = Product.objects.create(store=self.store, name="Bread", base_price=Decimal("60.00"))
        self.variant = ProductVariant.objects.create(product=product, sku="BREAD-LOAF")

    def test_pos_order_without_customer(self):
        order = Order.objects.create(store=self.store, channel=Order.Channel.POS)
        self.assertIsNone(order.customer)
        self.assertEqual(order.status, Order.Status.PENDING)

    def test_order_item_snapshots_price(self):
        order = Order.objects.create(store=self.store, channel=Order.Channel.POS)
        item = OrderItem.objects.create(order=order, variant=self.variant, quantity=2, unit_price=Decimal("60.00"))
        self.assertEqual(item.line_total, Decimal("120.00"))

    def test_online_order_with_customer(self):
        customer = Customer.objects.create(store=self.store, name="Jane W.", email="jane@example.com")
        order = Order.objects.create(store=self.store, channel=Order.Channel.ONLINE, customer=customer)
        self.assertEqual(order.customer.name, "Jane W.")

class OrderServiceTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(username="owner6", email="owner6@example.com", password="x")
        self.store = Store.objects.create(owner=owner, name="Shop F", slug="shop-f")
        product = Product.objects.create(store=self.store, name="Milk 1L", base_price=Decimal("120.00"))
        self.variant = ProductVariant.objects.create(product=product, sku="MILK-1L")
        from apps.inventory.services import record_stock_movement
        from apps.inventory.models import StockMovement
        record_stock_movement(
            variant=self.variant, movement_type=StockMovement.MovementType.PURCHASE, quantity_change=20
        )

    def test_add_item_decrements_stock_and_updates_total(self):
        order = Order.objects.create(store=self.store, channel=Order.Channel.POS)
        add_item_to_order(order=order, variant=self.variant, quantity=3)

        self.variant.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 17)
        self.assertEqual(order.total, Decimal("360.00"))  # 3 x 120.00

    def test_insufficient_stock_rolls_back_everything(self):
        order = Order.objects.create(store=self.store, channel=Order.Channel.POS)
        with self.assertRaises(InsufficientStockError):
            add_item_to_order(order=order, variant=self.variant, quantity=999)

        self.variant.refresh_from_db()
        order.refresh_from_db()
        # Nothing should have changed — no OrderItem, no stock change, no total change.
        self.assertEqual(order.items.count(), 0)
        self.assertEqual(self.variant.stock_quantity, 20)
        self.assertEqual(order.total, Decimal("0.00"))
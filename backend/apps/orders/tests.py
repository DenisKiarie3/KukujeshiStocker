from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.models import Store
from apps.inventory.models import Product, ProductVariant
from .models import Customer, Order, OrderItem

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
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .models import Store, StoreStaff

User = get_user_model()


class StoreModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner1", email="owner1@example.com", password="x")

    def test_create_store(self):
        store = Store.objects.create(owner=self.owner, name="Mama Njeri's Shop", slug="mama-njeris-shop")
        self.assertEqual(store.currency, "KES")

    def test_staff_role_unique_per_store(self):
        store = Store.objects.create(owner=self.owner, name="Shop A", slug="shop-a")
        staffer = User.objects.create_user(username="cashier1", email="cashier1@example.com", password="x")
        StoreStaff.objects.create(store=store, user=staffer, role=StoreStaff.Role.CASHIER)
        with self.assertRaises(IntegrityError):
            StoreStaff.objects.create(store=store, user=staffer, role=StoreStaff.Role.MANAGER)
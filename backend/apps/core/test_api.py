from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Store

User = get_user_model()


class StoreAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="apiowner1", email="apiowner1@example.com", password="x")
        self.other_user = User.objects.create_user(username="apiowner2", email="apiowner2@example.com", password="x")
        self.store = Store.objects.create(owner=self.owner, name="API Shop", slug="api-shop")

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get("/api/v1/stores/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_sees_their_store(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/v1/stores/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_other_user_does_not_see_this_store(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get("/api/v1/stores/")
        self.assertEqual(len(response.data), 0)

    def test_create_store_sets_owner_automatically(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post("/api/v1/stores/", {"name": "New Shop", "slug": "new-shop"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], self.owner.pk)
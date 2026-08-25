# backend/apps/users/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_with_unique_email(self):
        user = User.objects.create_user(
            username="shopowner1",
            email="owner@example.com",
            password="testpass123",
        )
        self.assertEqual(user.email, "owner@example.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_email_must_be_unique(self):
        User.objects.create_user(username="a", email="dup@example.com", password="x")
        with self.assertRaises(Exception):
            User.objects.create_user(username="b", email="dup@example.com", password="y")

class AuthAPITests(APITestCase):
    def setUp(self):
        # Auth endpoints are throttled (5/min) — clearing the cache before
        # each test prevents throttle state from one test bleeding into
        # the next and causing spurious 429s.
        cache.clear()
        self.user = User.objects.create_user(
            username="authuser1", email="authuser1@example.com", password="StrongPass123!"
        )

    def test_register_creates_user_and_sets_refresh_cookie(self):
        response = self.client.post("/api/v1/auth/register/", {
            "username": "newuser1", "email": "newuser1@example.com", "password": "AnotherStrongPass456!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["refresh_token"]["httponly"])

    def test_register_rejects_weak_password(self):
        response = self.client.post("/api/v1/auth/register/", {
            "username": "weakuser", "email": "weak@example.com", "password": "123"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_correct_credentials(self):
        response = self.client.post("/api/v1/auth/login/", {
            "username": "authuser1", "password": "StrongPass123!"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh_token", response.cookies)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post("/api/v1/auth/login/", {
            "username": "authuser1", "password": "wrongpass"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_without_cookie_fails(self):
        response = self.client.post("/api/v1/auth/refresh/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_with_cookie_but_missing_csrf_header_fails(self):
        self.client.post("/api/v1/auth/login/", {"username": "authuser1", "password": "StrongPass123!"})
        response = self.client.post("/api/v1/auth/refresh/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_with_valid_cookie_and_csrf_header_succeeds(self):
        self.client.post("/api/v1/auth/login/", {"username": "authuser1", "password": "StrongPass123!"})
        csrf_token = self.client.cookies["csrftoken"].value
        response = self.client.post("/api/v1/auth/refresh/", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_cannot_be_reused_after_rotation(self):
        self.client.post("/api/v1/auth/login/", {"username": "authuser1", "password": "StrongPass123!"})
        csrf_token = self.client.cookies["csrftoken"].value
        old_refresh_value = self.client.cookies["refresh_token"].value

        self.client.post("/api/v1/auth/refresh/", HTTP_X_CSRFTOKEN=csrf_token)  # rotates the token

        self.client.cookies["refresh_token"] = old_refresh_value  # replay the now-blacklisted one
        response = self.client.post("/api/v1/auth/refresh/", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh_token(self):
        self.client.post("/api/v1/auth/login/", {"username": "authuser1", "password": "StrongPass123!"})
        csrf_token = self.client.cookies["csrftoken"].value
        refresh_value = self.client.cookies["refresh_token"].value

        logout_response = self.client.post("/api/v1/auth/logout/", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        self.client.cookies["refresh_token"] = refresh_value  # replay the logged-out token
        response = self.client.post("/api/v1/auth/refresh/", HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
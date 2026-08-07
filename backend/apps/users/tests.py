# backend/apps/users/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model

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
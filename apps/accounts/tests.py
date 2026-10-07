"""Accounts tests (Django auth)."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", email="m@example.com", password="StrongPass123!")

    def test_login_with_username(self):
        resp = self.client.post(reverse("admin-login"), {"username": "manager", "password": "StrongPass123!"})
        self.assertEqual(resp.status_code, 302)

    def test_login_with_email(self):
        resp = self.client.post(reverse("admin-login"), {"username": "m@example.com", "password": "StrongPass123!"})
        self.assertEqual(resp.status_code, 302)

    def test_login_wrong_password(self):
        resp = self.client.post(reverse("admin-login"), {"username": "manager", "password": "wrong"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Invalid")

    def test_admin_requires_login(self):
        resp = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(resp.status_code, 302)

    def test_password_is_hashed(self):
        self.assertNotEqual(self.user.password, "StrongPass123!")
        self.assertTrue(self.user.check_password("StrongPass123!"))

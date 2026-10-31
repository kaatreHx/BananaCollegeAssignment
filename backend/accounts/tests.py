from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    def register(self, **overrides):
        payload = {
            "name": "Manish",
            "email": "manish@example.com",
            "password": "StrongBanana42!",
            **overrides,
        }
        return self.client.post(reverse("register"), payload, format="json")

    def test_register_creates_player_and_tokens(self):
        response = self.register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["player"]["name"], "Manish")
        self.assertIn("access", response.data["tokens"])

    def test_register_rejects_duplicate_email(self):
        self.register()
        response = self.register(name="Other")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_by_email(self):
        self.register()
        response = self.client.post(
            reverse("login"),
            {"email": "manish@example.com", "password": "StrongBanana42!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_requires_token(self):
        self.assertEqual(self.client.get(reverse("me")).status_code, status.HTTP_401_UNAUTHORIZED)

# accounts/tests/test_api.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class AccountsAPITestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="jacob",
            email="jacob@example.com",
            password="strongpassword123"
        )
        # Log the user in
        self.client.login(username="jacob", password="strongpassword123")

    def test_get_profile(self):
        """Test retrieving user profile details"""
        url = reverse("api_profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "jacob")

    def test_update_profile(self):
        """Test updating user profile"""
        url = reverse("api_profile_update")
        data = {
            "username": "jacob_updated",
            "email": "jacob_updated@example.com"
        }
        response = self.client.post(url, data)  # use POST for standard TestCase

        self.assertEqual(response.status_code, 200)
        # Refresh from DB
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "jacob_updated")
        self.assertEqual(self.user.email, "jacob_updated@example.com")

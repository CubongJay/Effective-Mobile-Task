import bcrypt
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.mocks.permissions import EXTRA_PERMISSIONS
from users.models import Users


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        EXTRA_PERMISSIONS.clear()

    def _create_user(self, email, password="password123", role="user"):
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        return Users.objects.create(
            first_name="Test",
            last_name="User",
            email=email,
            password=hashed,
            role=role,
        )

    def _auth_headers(self, email, password="password123"):
        response = self.client.post(
            "/api/token/",
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.data['access']}"}

    def test_register_and_login(self):
        response = self.client.post(
            "/api/users/create/",
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "password": "password123",
                "confirm_password": "password123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        token_response = self.client.post(
            "/api/token/",
            {"email": "jane@example.com", "password": "password123"},
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_response.data)
        self.assertEqual(token_response.data["email"], "jane@example.com")

    def test_list_users_requires_authentication(self):
        self._create_user("listed@example.com")
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        auth = self._auth_headers("listed@example.com")
        response = self.client.get("/api/users/", **auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_document_owner_can_view(self):
        owner = self._create_user("owner@example.com")
        auth = self._auth_headers("owner@example.com")

        response = self.client.get("/api/documents/2/", **auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 2)

    def test_non_owner_cannot_view_without_grant(self):
        self._create_user("owner@example.com")
        other = self._create_user("other@example.com")
        auth = self._auth_headers("other@example.com")

        response = self.client.get("/api/documents/2/", **auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_grant_document_access(self):
        self._create_user("owner@example.com")
        other = self._create_user("other@example.com")
        admin = self._create_user("admin@example.com", role="admin")
        admin_auth = self._auth_headers("admin@example.com")
        other_auth = self._auth_headers("other@example.com")

        grant_response = self.client.post(
            "/api/admin/permissions/grant/",
            {
                "user_id": other.id,
                "document_id": 2,
                "can_view": True,
                "can_edit": False,
                "can_delete": False,
            },
            format="json",
            **admin_auth,
        )
        self.assertEqual(grant_response.status_code, status.HTTP_201_CREATED)

        view_response = self.client.get("/api/documents/2/", **other_auth)
        self.assertEqual(view_response.status_code, status.HTTP_200_OK)

    def test_user_update_returns_400_on_invalid_data(self):
        user = self._create_user("patch@example.com")
        auth = self._auth_headers("patch@example.com")

        response = self.client.patch(
            f"/api/users/{user.id}/update/",
            {"email": "not-an-email"},
            format="json",
            **auth,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_cannot_access_admin_permissions(self):
        user = self._create_user("regular@example.com")
        auth = self._auth_headers("regular@example.com")

        response = self.client.get("/api/admin/permissions/", **auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

"""
Integration tests for authentication API endpoints.
Constitution Principle VI: Test-Driven Phase Completion
Tests: T006-T008 (Authentication & Security)
"""
import pytest
from fastapi.testclient import TestClient


class TestUserRegistration:
    """Test user registration endpoint."""

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_user_success(self, client: TestClient):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePassword123!"
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_user_duplicate_email(self, client: TestClient, registered_user):
        """Test registration with duplicate email fails."""
        user_data = {
            "email": registered_user["email"],
            "password": "AnotherPassword456!"
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePassword123!"
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.auth
    def test_register_user_missing_password(self, client: TestClient):
        """Test registration without password fails."""
        user_data = {
            "email": "test@example.com"
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422


class TestUserLogin:
    """Test user login endpoint."""

    @pytest.mark.integration
    @pytest.mark.auth
    def test_login_valid_credentials(self, client: TestClient, registered_user):
        """Test login with valid credentials."""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.integration
    @pytest.mark.auth
    def test_login_invalid_password(self, client: TestClient, registered_user):
        """Test login with incorrect password."""
        login_data = {
            "email": registered_user["email"],
            "password": "WrongPassword123!"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.auth
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.auth
    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing credentials."""
        response = client.post("/api/v1/auth/login", json={})

        assert response.status_code == 422


class TestTokenRefresh:
    """Test token refresh endpoint."""

    @pytest.mark.integration
    @pytest.mark.auth
    def test_refresh_token_valid(self, client: TestClient, registered_user):
        """Test refreshing token with valid refresh token."""
        refresh_data = {
            "refresh_token": registered_user["refresh_token"]
        }

        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.integration
    @pytest.mark.auth
    def test_refresh_token_invalid(self, client: TestClient):
        """Test refreshing with invalid token."""
        refresh_data = {
            "refresh_token": "invalid.token.here"
        }

        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 401


class TestGetCurrentUser:
    """Test get current user endpoint."""

    @pytest.mark.integration
    @pytest.mark.auth
    def test_get_me_authenticated(self, client: TestClient, auth_headers, registered_user):
        """Test getting current user with valid token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == registered_user["user_id"]
        assert data["email"] == registered_user["email"]

    @pytest.mark.integration
    @pytest.mark.auth
    def test_get_me_unauthenticated(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 403
        assert "detail" in response.json()

    @pytest.mark.integration
    @pytest.mark.auth
    def test_get_me_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}

        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401


class TestAuthenticationMiddleware:
    """Test authentication middleware protection."""

    @pytest.mark.integration
    @pytest.mark.auth
    def test_protected_endpoint_requires_auth(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        # Ally types endpoint requires auth
        response = client.get("/api/v1/ally-types")

        assert response.status_code == 403

    @pytest.mark.integration
    @pytest.mark.auth
    def test_public_endpoints_no_auth_required(self, client: TestClient):
        """Test that public endpoints work without auth."""
        # Health check should be public
        response = client.get("/api/v1/health")

        assert response.status_code == 200

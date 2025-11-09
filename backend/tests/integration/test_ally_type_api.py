"""
Integration tests for ally type API endpoints.
Constitution Principle VI: Test-Driven Phase Completion
Tests: T018-T022 (Ally Type CRUD)
"""
import pytest
from fastapi.testclient import TestClient


class TestAllyTypeCreation:
    """Test ally type creation endpoint."""

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_create_ally_type_success(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test successful ally type creation."""
        response = client.post(
            "/api/v1/ally-types", json=sample_ally_type_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_ally_type_data["name"]
        assert data["keywords"] == sample_ally_type_data["keywords"]
        assert data["is_active"] is True

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_create_ally_type_unauthenticated(self, client: TestClient, sample_ally_type_data):
        """Test ally type creation without authentication."""
        response = client.post("/api/v1/ally-types",
                               json=sample_ally_type_data)

        assert response.status_code == 403

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_create_ally_type_duplicate_name(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test creating ally type with duplicate name for same user."""
        # Create first
        client.post("/api/v1/ally-types",
                    json=sample_ally_type_data, headers=auth_headers)

        # Try to create duplicate
        response = client.post(
            "/api/v1/ally-types", json=sample_ally_type_data, headers=auth_headers)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_create_ally_type_missing_required_fields(self, client: TestClient, auth_headers):
        """Test creation with missing required fields."""
        incomplete_data = {
            "name": "Test Ally"
            # Missing keywords, criteria
        }

        response = client.post("/api/v1/ally-types",
                               json=incomplete_data, headers=auth_headers)

        assert response.status_code == 422


class TestAllyTypeRetrieval:
    """Test ally type retrieval endpoints."""

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_list_ally_types(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test listing user's ally types."""
        # Create a few ally types
        client.post("/api/v1/ally-types",
                    json=sample_ally_type_data, headers=auth_headers)

        data2 = sample_ally_type_data.copy()
        data2["name"] = "Different Ally"
        client.post("/api/v1/ally-types", json=data2, headers=auth_headers)

        # List all
        response = client.get("/api/v1/ally-types", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_list_ally_types_filter_by_active(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test filtering ally types by is_active status."""
        # Create active ally type
        create_response = client.post(
            "/api/v1/ally-types", json=sample_ally_type_data, headers=auth_headers)
        ally_id = create_response.json()["id"]

        # Soft delete it
        client.delete(f"/api/v1/ally-types/{ally_id}", headers=auth_headers)

        # List only active
        response = client.get(
            "/api/v1/ally-types?is_active=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Deleted ally type should not appear
        assert all(ally["is_active"] for ally in data)

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_get_ally_type_by_id(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test retrieving specific ally type."""
        create_response = client.post(
            "/api/v1/ally-types", json=sample_ally_type_data, headers=auth_headers)
        ally_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/ally-types/{ally_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ally_id
        assert data["name"] == sample_ally_type_data["name"]

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_get_ally_type_not_found(self, client: TestClient, auth_headers):
        """Test retrieving non-existent ally type."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.get(
            f"/api/v1/ally-types/{fake_id}", headers=auth_headers)

        assert response.status_code == 404


class TestAllyTypeUpdate:
    """Test ally type update endpoint."""

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_update_ally_type_success(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test successful ally type update."""
        create_response = client.post(
            "/api/v1/ally-types", json=sample_ally_type_data, headers=auth_headers)
        ally_id = create_response.json()["id"]

        update_data = {
            "name": "Updated AI Researchers",
            "keywords": ["AI", "ML", "deep learning", "NLP"]
        }

        response = client.put(
            f"/api/v1/ally-types/{ally_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated AI Researchers"
        assert len(data["keywords"]) == 4

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_update_ally_type_not_owned(self, client: TestClient, test_user_data, sample_ally_type_data):
        """Test that users cannot update other users' ally types."""
        # User 1 creates ally type
        user1_response = client.post(
            "/api/v1/auth/register", json=test_user_data)
        user1_token = user1_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        create_response = client.post(
            "/api/v1/ally-types", json=sample_ally_type_data, headers=user1_headers)
        ally_id = create_response.json()["id"]

        # User 2 tries to update
        user2_data = {"email": "user2@example.com", "password": "Password456!"}
        user2_response = client.post("/api/v1/auth/register", json=user2_data)
        user2_token = user2_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        update_data = {"name": "Hacked Name"}
        response = client.put(
            f"/api/v1/ally-types/{ally_id}", json=update_data, headers=user2_headers)

        assert response.status_code == 404


class TestAllyTypeDeletion:
    """Test ally type deletion endpoint."""

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_delete_ally_type_soft_delete(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test soft deletion (sets is_active=False)."""
        create_response = client.post(
            "/api/v1/ally-types", json=sample_ally_type_data, headers=auth_headers)
        ally_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/ally-types/{ally_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify it's soft deleted (is_active=False)
        get_response = client.get(
            f"/api/v1/ally-types/{ally_id}", headers=auth_headers)
        if get_response.status_code == 200:
            assert get_response.json()["is_active"] is False

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_delete_ally_type_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent ally type."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.delete(
            f"/api/v1/ally-types/{fake_id}", headers=auth_headers)

        assert response.status_code == 404


class TestAllyTypeImportExport:
    """Test ally type import/export endpoints (FR-014)."""

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_export_ally_types(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test exporting ally types as JSON."""
        # Create ally types
        client.post("/api/v1/ally-types",
                    json=sample_ally_type_data, headers=auth_headers)

        response = client.get("/api/v1/ally-types/export",
                              headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "ally_types" in data
        assert "version" in data
        assert len(data["ally_types"]) >= 1

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_import_ally_types(self, client: TestClient, auth_headers):
        """Test importing ally types from JSON."""
        import_data = {
            "ally_types": [
                {
                    "name": "Imported Ally",
                    "keywords": ["keyword1", "keyword2"],
                    "criteria": "Test criteria",
                    "search_parameters": {}
                }
            ]
        }

        response = client.post("/api/v1/ally-types/import",
                               json=import_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["imported"] >= 1
        assert data["skipped"] >= 0

    @pytest.mark.integration
    @pytest.mark.ally_type
    def test_import_skip_duplicates(self, client: TestClient, auth_headers, sample_ally_type_data):
        """Test that import skips duplicate names."""
        # Create existing ally type
        client.post("/api/v1/ally-types",
                    json=sample_ally_type_data, headers=auth_headers)

        # Try to import same name
        import_data = {
            "ally_types": [sample_ally_type_data]
        }

        response = client.post("/api/v1/ally-types/import",
                               json=import_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["skipped"] >= 1

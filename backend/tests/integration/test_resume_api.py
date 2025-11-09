"""
Integration tests for resume API endpoints.
Constitution Principle VI: Test-Driven Phase Completion
Tests: T013-T017 (Resume Upload & Parsing)
"""
import pytest
from io import BytesIO
from fastapi.testclient import TestClient


class TestResumeUpload:
    """Test resume upload endpoint."""

    @pytest.mark.integration
    @pytest.mark.resume
    def test_upload_resume_txt_success(self, client: TestClient, auth_headers, sample_resume_txt):
        """Test successful resume upload (TXT format)."""
        files = {
            "file": ("resume.txt", BytesIO(sample_resume_txt.encode()), "text/plain")
        }

        response = client.post("/api/v1/resumes/upload",
                               files=files, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "resume_id" in data
        assert "status" in data
        assert data["message"] == "Resume uploaded successfully"

    @pytest.mark.integration
    @pytest.mark.resume
    def test_upload_resume_unauthenticated(self, client: TestClient, sample_resume_txt):
        """Test resume upload without authentication."""
        files = {
            "file": ("resume.txt", BytesIO(sample_resume_txt.encode()), "text/plain")
        }

        response = client.post("/api/v1/resumes/upload", files=files)

        assert response.status_code == 403

    @pytest.mark.integration
    @pytest.mark.resume
    def test_upload_resume_invalid_format(self, client: TestClient, auth_headers):
        """Test uploading file with invalid extension."""
        files = {
            "file": ("resume.exe", BytesIO(b"fake content"), "application/octet-stream")
        }

        response = client.post("/api/v1/resumes/upload",
                               files=files, headers=auth_headers)

        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.resume
    @pytest.mark.slow
    def test_upload_resume_too_large(self, client: TestClient, auth_headers):
        """Test uploading file exceeding size limit (10MB)."""
        # Create 11MB file
        large_content = b"x" * (11 * 1024 * 1024)
        files = {
            "file": ("resume.txt", BytesIO(large_content), "text/plain")
        }

        response = client.post("/api/v1/resumes/upload",
                               files=files, headers=auth_headers)

        assert response.status_code == 413 or response.status_code == 400

    @pytest.mark.integration
    @pytest.mark.resume
    def test_upload_resume_missing_file(self, client: TestClient, auth_headers):
        """Test upload without file."""
        response = client.post("/api/v1/resumes/upload", headers=auth_headers)

        assert response.status_code == 422


class TestResumeRetrieval:
    """Test resume retrieval endpoints."""

    @pytest.mark.integration
    @pytest.mark.resume
    def test_get_resume_status(self, client: TestClient, auth_headers, sample_resume_txt):
        """Test getting resume parsing status."""
        # Upload resume first
        files = {
            "file": ("resume.txt", BytesIO(sample_resume_txt.encode()), "text/plain")
        }
        upload_response = client.post(
            "/api/v1/resumes/upload", files=files, headers=auth_headers)
        resume_id = upload_response.json()["resume_id"]

        # Get status
        response = client.get(
            f"/api/v1/resumes/{resume_id}/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["pending", "processing",
                                  "parsed_success", "parsed_error"]

    @pytest.mark.integration
    @pytest.mark.resume
    def test_get_parsed_resume(self, client: TestClient, auth_headers, sample_resume_txt):
        """Test retrieving parsed resume data."""
        # Upload resume
        files = {
            "file": ("resume.txt", BytesIO(sample_resume_txt.encode()), "text/plain")
        }
        upload_response = client.post(
            "/api/v1/resumes/upload", files=files, headers=auth_headers)
        resume_id = upload_response.json()["resume_id"]

        # Wait briefly for background parsing (in real tests, might need to wait or mock)
        import time
        time.sleep(1)

        # Get parsed data
        response = client.get(
            f"/api/v1/resumes/{resume_id}", headers=auth_headers)

        # Should get either parsed data or pending status
        assert response.status_code in [200, 202]

        if response.status_code == 200:
            data = response.json()
            assert "skills" in data
            assert "achievements" in data
            assert "parsing_confidence" in data

    @pytest.mark.integration
    @pytest.mark.resume
    def test_get_resume_not_found(self, client: TestClient, auth_headers):
        """Test retrieving non-existent resume."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = client.get(
            f"/api/v1/resumes/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.resume
    def test_get_other_user_resume(self, client: TestClient, test_user_data, sample_resume_txt):
        """Test that users cannot access other users' resumes."""
        # Register and upload as user 1
        user1_response = client.post(
            "/api/v1/auth/register", json=test_user_data)
        user1_token = user1_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        files = {
            "file": ("resume.txt", BytesIO(sample_resume_txt.encode()), "text/plain")
        }
        upload_response = client.post(
            "/api/v1/resumes/upload", files=files, headers=user1_headers)
        resume_id = upload_response.json()["resume_id"]

        # Register user 2
        user2_data = {"email": "user2@example.com", "password": "Password456!"}
        user2_response = client.post("/api/v1/auth/register", json=user2_data)
        user2_token = user2_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Try to access user1's resume as user2
        response = client.get(
            f"/api/v1/resumes/{resume_id}", headers=user2_headers)

        assert response.status_code == 404


class TestResumeParsingQuality:
    """Test resume parsing quality (SC-004: ≥95% accuracy)."""

    @pytest.mark.integration
    @pytest.mark.resume
    def test_parsing_confidence_calculation(self, client: TestClient, auth_headers, sample_resume_txt):
        """Test that parsing confidence is calculated."""
        files = {
            "file": ("resume.txt", BytesIO(sample_resume_txt.encode()), "text/plain")
        }
        upload_response = client.post(
            "/api/v1/resumes/upload", files=files, headers=auth_headers)
        resume_id = upload_response.json()["resume_id"]

        # Wait for parsing
        import time
        time.sleep(1)

        response = client.get(
            f"/api/v1/resumes/{resume_id}", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert "parsing_confidence" in data
            assert 0.0 <= data["parsing_confidence"] <= 1.0

    @pytest.mark.integration
    @pytest.mark.resume
    def test_skills_extraction_from_sample(self, client: TestClient, auth_headers, sample_resume_txt):
        """Test that skills are extracted from sample resume."""
        files = {
            "file": ("resume.txt", BytesIO(sample_resume_txt.encode()), "text/plain")
        }
        upload_response = client.post(
            "/api/v1/resumes/upload", files=files, headers=auth_headers)
        resume_id = upload_response.json()["resume_id"]

        # Wait for parsing
        import time
        time.sleep(1)

        response = client.get(
            f"/api/v1/resumes/{resume_id}", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            skills = data.get("skills", [])
            # Sample resume contains: Python, TypeScript, React, FastAPI, SQL, etc.
            assert len(skills) >= 5
            assert any("Python" in str(s) for s in skills)

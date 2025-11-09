"""
Pytest configuration and shared fixtures for Phase 1 tests.
"""
from src.main import app
from src.core.database import Base, get_db
from src.core.config import settings
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
import pytest
import os
import sys
from pathlib import Path
from typing import Generator

# Add src to path for imports FIRST
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }


@pytest.fixture
def registered_user(client: TestClient, test_user_data):
    """Create and return a registered user with tokens."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()

    # Decode the access token to get user_id
    from jose import jwt
    from src.core.security import JWT_SECRET_KEY, JWT_ALGORITHM

    payload = jwt.decode(
        data["access_token"],
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM]
    )

    return {
        **test_user_data,
        "user_id": payload["user_id"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"]
    }


@pytest.fixture
def auth_headers(registered_user):
    """Return authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}


@pytest.fixture
def sample_resume_txt():
    """Sample resume text content."""
    return """John Doe
Senior Software Engineer

PROFESSIONAL EXPERIENCE
Uber Technologies Inc. | Senior Software Engineer | 2020-2023
- Led development of microservices architecture serving 10M+ daily users
- Improved API response time by 45% through optimization techniques
- Mentored team of 5 junior engineers

SKILLS
Python, TypeScript, React, FastAPI, SQL, PostgreSQL, Docker, Kubernetes, AWS, Microservices

EDUCATION
MIT | B.S. Computer Science | 2016-2020
"""


@pytest.fixture
def sample_ally_type_data():
    """Sample ally type data for testing."""
    return {
        "name": "AI Researchers",
        "keywords": ["machine learning", "neural networks", "deep learning", "AI"],
        "criteria": "Researchers focusing on cutting-edge AI and ML technologies",
        "search_parameters": {
            "platforms": ["github", "twitter", "linkedin"],
            "min_relevance": 0.7
        }
    }

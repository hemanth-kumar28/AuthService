"""
Test fixtures — sets up a PostgreSQL test database and provides
a test client + auth helpers.
"""

import os

# Force test database BEFORE any app imports
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5431/auth_service_test_db",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app


# ── Test DB engine ─────────────────────────────────────────────

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ── Fixtures ───────────────────────────────────────────────────


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables before tests, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """Truncate all tables between tests for isolation."""
    yield
    with test_engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE note_tags, notes, tags, refresh_tokens, users CASCADE"))
        conn.commit()


@pytest.fixture()
def client():
    """HTTP test client."""
    return TestClient(app)


@pytest.fixture()
def registered_user(client: TestClient) -> dict:
    """Register a user and return the full response data."""
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test@1234",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    return resp.json()["data"]


@pytest.fixture()
def auth_headers(registered_user: dict) -> dict:
    """Authorization headers for the registered user."""
    token = registered_user["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def second_user(client: TestClient) -> dict:
    """Register a second user for ownership tests."""
    payload = {
        "email": "other@example.com",
        "username": "otheruser",
        "password": "Other@1234",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    data["_headers"] = {
        "Authorization": f"Bearer {data['tokens']['access_token']}"
    }
    return data

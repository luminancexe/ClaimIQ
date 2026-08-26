"""Tests for ClaimIQ Phase 7 Backend Health endpoints."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db


class MockHealthyDb:
    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def execute(self, sql):
        pass

    def close(self):
        pass


def test_root_health_endpoint():
    """Verify GET /health returns 200 and HealthResponse envelope."""
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.7.0"
    assert "timestamp" in data
    assert "x-request-id" in response.headers


def test_api_v1_health_endpoint():
    """Verify GET /api/v1/health returns matching health payload."""
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.7.0"


def test_health_db_status_reflection():
    """Verify database_connected field reflects database state."""
    app = create_app()

    # When get_db yields None (disconnected)
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)
    res_disconnected = client.get("/health")
    assert res_disconnected.status_code == 200
    assert res_disconnected.json()["database_connected"] is False

    # When get_db yields healthy connection
    app.dependency_overrides[get_db] = lambda: MockHealthyDb()
    res_connected = client.get("/health")
    assert res_connected.status_code == 200
    assert res_connected.json()["database_connected"] is True

"""Tests for ClaimIQ Phase 7 Request Validation and Error responses."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db
from backend.services.auth import create_access_token


def _get_auth_headers():
    token = create_access_token("usr-admin-001", "admin", "ADMIN")
    return {"Authorization": f"Bearer {token}"}


def test_invalid_login_missing_fields():
    """Verify missing username or password returns 422 with structured error."""
    app = create_app()
    client = TestClient(app)

    res = client.post("/api/v1/auth/login", json={})
    assert res.status_code == 422
    data = res.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "request_id" in data


def test_invalid_trend_interval_rejected():
    """Verify invalid trend interval returns 400 Bad Request."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/analytics/trends?interval=yearly", headers=_get_auth_headers())
    assert res.status_code == 400
    assert res.json()["error_code"] == "BAD_REQUEST"


def test_invalid_id_type_in_path():
    """Verify string passed to integer path parameter returns 422 validation error."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/claims/not-a-number", headers=_get_auth_headers())
    assert res.status_code == 422
    assert res.json()["error_code"] == "VALIDATION_ERROR"

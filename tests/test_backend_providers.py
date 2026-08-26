"""Tests for ClaimIQ Phase 7 Providers endpoints."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db
from backend.services.auth import create_access_token


def _get_auth_headers():
    token = create_access_token("usr-admin-001", "admin", "ADMIN")
    return {"Authorization": f"Bearer {token}"}


def test_list_providers_empty_when_no_db():
    """Verify list providers returns empty PaginatedResponse when DB offline."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/providers", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_get_provider_detail_not_found():
    """Verify nonexistent provider returns 404."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/providers/9999", headers=_get_auth_headers())
    assert res.status_code == 404


def test_get_provider_scorecard_simulated():
    """Verify provider scorecard endpoint returns scorecard structure."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/providers/1/scorecard", headers=_get_auth_headers())
    # Provider 1 is the simulated mock scorecard provider in dry-run mode
    assert res.status_code == 200
    data = res.json()
    assert data["provider_id"] == 1
    assert "payment_rate" in data
    assert "dq_score" in data

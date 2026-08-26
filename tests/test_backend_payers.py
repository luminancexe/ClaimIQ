"""Tests for ClaimIQ Phase 7 Payers endpoints."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db
from backend.services.auth import create_access_token


def _get_auth_headers():
    token = create_access_token("usr-admin-001", "admin", "ADMIN")
    return {"Authorization": f"Bearer {token}"}


def test_list_payers_empty_when_no_db():
    """Verify list payers returns empty PaginatedResponse when DB offline."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/payers", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_get_payer_detail_not_found():
    """Verify nonexistent payer returns 404."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/payers/9999", headers=_get_auth_headers())
    assert res.status_code == 404


def test_get_payer_scorecard_simulated():
    """Verify payer scorecard endpoint returns scorecard structure."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/payers/1/scorecard", headers=_get_auth_headers())
    # Payer 1 is the simulated mock scorecard payer in dry-run mode
    assert res.status_code == 200
    data = res.json()
    assert data["payer_id"] == 1
    assert "denial_rate" in data
    assert "contractual_adjustment_ratio" in data

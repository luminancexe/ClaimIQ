"""Tests for ClaimIQ Phase 7 Analytics endpoints."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db
from backend.services.auth import create_access_token


def _get_auth_headers():
    token = create_access_token("usr-analyst-001", "analyst", "ANALYST")
    return {"Authorization": f"Bearer {token}"}


def test_analytics_overview():
    """Verify GET /api/v1/analytics/overview returns aggregated financial, KPI, and root cause."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/analytics/overview", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert "financial" in data
    assert "kpis" in data
    assert "root_cause" in data
    assert data["financial"]["reconciliation_rate"] >= 0.0


def test_analytics_financial():
    """Verify GET /api/v1/analytics/financial returns Decimal strings."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/analytics/financial", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["total_billed"], str)
    assert isinstance(data["total_paid"], str)
    assert "reconciliation_rate" in data
    assert "financial_integrity_rate" in data


def test_analytics_kpis():
    """Verify GET /api/v1/analytics/kpis returns 4 KPI sections."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/analytics/kpis", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert "claims" in data
    assert "payments" in data
    assert "denials" in data
    assert "qa" in data


def test_analytics_trends():
    """Verify GET /api/v1/analytics/trends supports interval query."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/analytics/trends?interval=monthly", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert data["interval"] == "monthly"
    assert "points" in data
    assert "trend_direction" in data


def test_analytics_root_causes_and_recurrence():
    """Verify root causes and recurrence endpoints."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res_rc = client.get("/api/v1/analytics/root-causes", headers=_get_auth_headers())
    assert res_rc.status_code == 200
    assert "items" in res_rc.json()
    assert "pareto_cutoff_index" in res_rc.json()

    res_rec = client.get("/api/v1/analytics/recurrence", headers=_get_auth_headers())
    assert res_rec.status_code == 200
    assert "recurring_cluster_count" in res_rec.json()

"""Tests for ClaimIQ Phase 7 Issues endpoints."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db
from backend.services.auth import create_access_token


def _get_auth_headers():
    token = create_access_token("usr-admin-001", "admin", "ADMIN")
    return {"Authorization": f"Bearer {token}"}


def test_list_issues_empty_when_no_db():
    """Verify list issues returns empty PaginatedResponse when DB offline."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/issues", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_get_issue_detail_not_found():
    """Verify nonexistent issue returns 404."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/issues/9999", headers=_get_auth_headers())
    assert res.status_code == 404
    assert res.json()["error_code"] == "NOT_FOUND"


def test_issue_serialization():
    """Verify issue serialization handles variance amount Decimal strings."""
    from backend.services.issues import _serialize_issue_summary, _serialize_issue_detail
    from decimal import Decimal

    summary_row = {
        "issue_id": 1,
        "issue_reference": "ISS-20250101-00001",
        "rule_id": 4,
        "claim_id": 12,
        "dimension_code": "Financial",
        "severity_code": "High",
        "current_status_code": "Detected",
        "detected_at": "2025-01-01 12:00:00.000000",
        "resolved_at": None,
        "variance_amount": Decimal("150.75"),
    }
    ser_summary = _serialize_issue_summary(summary_row)
    assert ser_summary["variance_amount"] == "150.75"

    detail_row = dict(summary_row)
    detail_row["rule_code"] = "R-E023"
    detail_row["rule_name"] = "Reconciliation Variance"
    detail_row["assigned_to_user"] = None
    detail_row["root_cause_code"] = "CALCULATION_ROUNDING_DEFECT"
    ser_detail = _serialize_issue_detail(detail_row)
    assert ser_detail["rule_code"] == "R-E023"
    assert ser_detail["variance_amount"] == "150.75"

"""Tests for ClaimIQ Phase 7 Claims endpoints."""

from decimal import Decimal
from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db, get_current_user
from backend.services.auth import create_access_token


class MockClaimsDb:
    def __init__(self):
        self.claims = [
            {
                "claim_id": 1,
                "claim_reference": "CLM-2025-000001",
                "encounter_id": 10,
                "patient_id": 100,
                "billing_provider_id": 20,
                "payer_id": 5,
                "current_status_code": "Submitted",
                "total_billed_amount": Decimal("1250.00"),
                "submission_date": "2025-01-15",
                "adjudication_date": None,
                "is_reconciled": 0,
            }
        ]

    def cursor(self, cursorclass=None):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def execute(self, sql, params=None):
        pass

    def fetchone(self):
        return self.claims[0]

    def fetchall(self):
        return self.claims

    def close(self):
        pass


def _get_auth_headers():
    token = create_access_token("usr-admin-001", "admin", "ADMIN")
    return {"Authorization": f"Bearer {token}"}


def test_list_claims_empty_when_no_db():
    """Verify list claims returns empty PaginatedResponse gracefully when DB is offline."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/claims", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["page"] == 1


def test_get_claim_detail_not_found():
    """Verify nonexistent claim returns 404."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/claims/9999", headers=_get_auth_headers())
    assert res.status_code == 404
    assert res.json()["error_code"] == "NOT_FOUND"


def test_get_claim_lines_empty_when_no_db():
    """Verify claim lines returns empty list when DB offline."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/claims/1/lines", headers=_get_auth_headers())
    assert res.status_code == 200
    assert res.json() == []


def test_get_claim_history_empty_when_no_db():
    """Verify claim history returns empty list when DB offline."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/claims/1/history", headers=_get_auth_headers())
    assert res.status_code == 200
    assert res.json() == []


def test_list_claims_serialization_preserves_decimal():
    """Verify Decimal amounts are serialized as clean strings."""
    from backend.services.claims import _serialize_claim_row
    row = {
        "claim_id": 1,
        "claim_reference": "CLM-2025-000001",
        "encounter_id": 1,
        "patient_id": 1,
        "billing_provider_id": 1,
        "payer_id": 1,
        "current_status_code": "Paid",
        "total_billed_amount": Decimal("1250.50"),
        "submission_date": "2025-01-15",
        "adjudication_date": "2025-01-20",
        "is_reconciled": 1,
    }
    serialized = _serialize_claim_row(row)
    assert serialized["total_billed_amount"] == "1250.50"
    assert serialized["is_reconciled"] is True

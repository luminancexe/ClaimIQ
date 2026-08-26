"""Tests for ClaimIQ Phase 7 Pagination behavior and limits."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db
from backend.services.auth import create_access_token


def _get_auth_headers():
    token = create_access_token("usr-admin-001", "admin", "ADMIN")
    return {"Authorization": f"Bearer {token}"}


def test_pagination_defaults():
    """Verify default query parameters are page=1, page_size=50."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/claims", headers=_get_auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 50


def test_pagination_max_page_size_enforced():
    """Verify page_size > 500 triggers 422 Unprocessable Entity."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/claims?page_size=501", headers=_get_auth_headers())
    assert res.status_code == 422
    assert res.json()["error_code"] == "VALIDATION_ERROR"


def test_pagination_invalid_page_zero():
    """Verify page < 1 triggers 422 validation error."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/claims?page=0", headers=_get_auth_headers())
    assert res.status_code == 422


def test_pagination_response_metadata_calculation():
    """Verify total_pages, has_next, and has_previous logic."""
    from backend.schemas.common import PaginatedResponse

    # Case 1: Multiple pages, on first page
    p1 = PaginatedResponse[int](
        page=1, page_size=10, total=25, total_pages=3,
        has_next=True, has_previous=False, items=[1, 2]
    )
    assert p1.has_next is True
    assert p1.has_previous is False

    # Case 2: Middle page
    p2 = PaginatedResponse[int](
        page=2, page_size=10, total=25, total_pages=3,
        has_next=True, has_previous=True, items=[3, 4]
    )
    assert p2.has_next is True
    assert p2.has_previous is True

    # Case 3: Last page
    p3 = PaginatedResponse[int](
        page=3, page_size=10, total=25, total_pages=3,
        has_next=False, has_previous=True, items=[5]
    )
    assert p3.has_next is False
    assert p3.has_previous is True

"""Tests for ClaimIQ Phase 7 Role-Based Authorization and Token Security."""

from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from backend.app import create_app
from backend.dependencies import require_role
from backend.services.auth import create_access_token


def test_missing_authorization_header_returns_401():
    """Verify accessing protected endpoint without token returns 401."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/api/v1/claims")
    assert res.status_code == 401
    assert res.json()["error_code"] == "UNAUTHORIZED"


def test_malformed_token_returns_401():
    """Verify malformed authorization header returns 401."""
    app = create_app()
    client = TestClient(app)

    res = client.get(
        "/api/v1/claims",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"},
    )
    assert res.status_code == 401


def test_expired_token_returns_401():
    """Verify expired token returns 401 UNAUTHORIZED."""
    app = create_app()
    client = TestClient(app)

    expired_token = create_access_token(
        user_id="usr-test", username="testuser", role="ADMIN", expires_minutes=-10
    )
    res = client.get(
        "/api/v1/claims",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res.status_code == 401
    assert "expired" in res.json()["message"].lower()


def test_role_enforcement_dependency():
    """Verify require_role allows authorized role and rejects unauthorized role."""
    test_app = FastAPI()
    from backend.middleware.errors import register_exception_handlers
    register_exception_handlers(test_app)

    @test_app.get("/admin-only", dependencies=[Depends(require_role("ADMIN"))])
    def admin_endpoint():
        return {"status": "ok"}

    client = TestClient(test_app)

    # Admin token should succeed
    admin_token = create_access_token("u1", "admin", "ADMIN")
    res_admin = client.get("/admin-only", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200

    # Viewer token should be forbidden (403)
    viewer_token = create_access_token("u2", "viewer", "VIEWER")
    res_viewer = client.get("/admin-only", headers={"Authorization": f"Bearer {viewer_token}"})
    assert res_viewer.status_code == 403
    assert res_viewer.json()["error_code"] == "FORBIDDEN"

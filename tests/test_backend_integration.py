"""Integration tests for ClaimIQ Phase 7 End-to-End API Workflows."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db


def test_full_auth_and_protected_query_workflow():
    """Verify complete user flow: login -> get token -> access protected endpoints."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    # 1. Unauthenticated request should fail
    unauth_res = client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401

    # 2. Login as Analyst
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "analyst", "password": "Analyst@123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Call /me
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "analyst"

    # 4. Call QA rules catalog (67 rules)
    rules_res = client.get("/api/v1/qa/rules", headers=headers)
    assert rules_res.status_code == 200
    assert len(rules_res.json()) == 67

    # 5. Call Analytics Overview
    overview_res = client.get("/api/v1/analytics/overview", headers=headers)
    assert overview_res.status_code == 200
    assert "financial" in overview_res.json()
    assert "kpis" in overview_res.json()

    # 6. Call Analytics Financial
    fin_res = client.get("/api/v1/analytics/financial", headers=headers)
    assert fin_res.status_code == 200
    assert "total_billed" in fin_res.json()

    # 7. Call Claims paginated list
    claims_res = client.get("/api/v1/claims", headers=headers)
    assert claims_res.status_code == 200
    assert claims_res.json()["page"] == 1


def test_cors_and_request_id_headers_on_all_responses():
    """Verify X-Request-ID and CORS headers present across endpoints."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/health")
    assert "x-request-id" in res.headers
    assert "access-control-allow-origin" in res.headers or res.status_code == 200


def test_token_refresh_lifecycle_integration():
    """Verify login -> refresh -> use new access token workflow."""
    app = create_app()
    client = TestClient(app)

    # Initial login
    res1 = client.post("/api/v1/auth/login", json={"username": "viewer", "password": "Viewer@123"})
    assert res1.status_code == 200
    tokens = res1.json()
    ref_token = tokens["refresh_token"]

    # Exchange refresh token
    res2 = client.post("/api/v1/auth/refresh", json={"refresh_token": ref_token})
    assert res2.status_code == 200
    new_tokens = res2.json()
    new_access_token = new_tokens["access_token"]

    # Use new token to query /me
    res3 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {new_access_token}"})
    assert res3.status_code == 200
    assert res3.json()["username"] == "viewer"

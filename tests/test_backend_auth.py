"""Tests for ClaimIQ Phase 7 Authentication and JWT endpoints."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    _USER_STORE,
    create_user,
)
from backend.config import BackendConfig


def test_password_hashing_and_verification():
    """Verify PBKDF2 hashing produces unique salts and verifies correctly."""
    pwd = "SecurePassword@123"
    hashed1 = hash_password(pwd)
    hashed2 = hash_password(pwd)

    assert hashed1.startswith("pbkdf2_sha256$")
    assert hashed1 != hashed2  # Random salt ensures non-identical hashes
    assert verify_password(pwd, hashed1) is True
    assert verify_password(pwd, hashed2) is True
    assert verify_password("WrongPassword", hashed1) is False


def test_login_success():
    """Verify valid credentials return access & refresh JWT tokens."""
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600


def test_login_invalid_credentials():
    """Verify invalid credentials return 401 UNAUTHORIZED."""
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"


def test_refresh_token_flow():
    """Verify valid refresh token can be exchanged for new token pair."""
    app = create_app()
    client = TestClient(app)

    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "analyst", "password": "Analyst@123"},
    )
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token_invalid():
    """Verify invalid or forged refresh token returns 401."""
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.jwt.token"},
    )
    assert response.status_code == 401


def test_get_me_endpoint():
    """Verify GET /api/v1/auth/me returns authenticated user profile."""
    app = create_app()
    client = TestClient(app)

    # Login to get token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "qa_reviewer", "password": "QaReviewer@123"},
    )
    token = login_res.json()["access_token"]

    # Call /me with Bearer token
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["username"] == "qa_reviewer"
    assert data["role"] == "QA_REVIEWER"
    assert "user_id" in data

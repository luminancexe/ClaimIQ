"""Tests for ClaimIQ Phase 7 Error Formatting and Sensitive Information Leak Prevention."""

from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from backend.app import create_app
from backend.middleware.errors import RequestIdMiddleware, register_exception_handlers
from backend.services.auth import create_access_token


def test_standardized_error_structure():
    """Verify error responses contain error_code, message, and request_id."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/api/v1/claims")  # Unauthenticated
    assert res.status_code == 401
    data = res.json()
    assert "error_code" in data
    assert "message" in data
    assert "request_id" in data
    assert data["request_id"].startswith("req-") or len(data["request_id"]) > 0


def test_client_request_id_echo():
    """Verify valid client-provided X-Request-ID is preserved and echoed."""
    app = create_app()
    client = TestClient(app)

    custom_id = "test-custom-request-id-12345"
    res = client.get("/health", headers={"X-Request-ID": custom_id})
    assert res.status_code == 200
    assert res.headers["X-Request-ID"] == custom_id


def test_internal_server_error_sanitization():
    """Verify 500 handler masks raw stack traces, SQL, and internal file paths."""
    test_app = FastAPI()
    test_app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(test_app)

    @test_app.get("/explode")
    def explode():
        raise RuntimeError("SELECT password_hash FROM sensitive_users WHERE secret = '12345'")

    client = TestClient(test_app, raise_server_exceptions=False)
    res = client.get("/explode")
    assert res.status_code == 500
    data = res.json()
    assert data["error_code"] == "INTERNAL_SERVER_ERROR"
    # Ensure sensitive SQL statement was masked
    assert "password_hash" not in data["message"]
    assert "sensitive_users" not in data["message"]
    assert "Traceback" not in data["message"]

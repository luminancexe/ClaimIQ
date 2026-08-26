"""Tests for ClaimIQ Phase 7 OpenAPI 3.x and Swagger documentation."""

from fastapi.testclient import TestClient
from backend.app import create_app


def test_openapi_json_schema():
    """Verify /openapi.json returns valid OpenAPI 3.x spec with ClaimIQ metadata."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"] == "ClaimIQ API"
    assert schema["info"]["version"] == "0.7.0"
    assert "paths" in schema
    assert len(schema["paths"]) >= 20


def test_openapi_tags_inventory():
    """Verify all 8 standard tags exist in OpenAPI spec."""
    app = create_app()
    client = TestClient(app)

    res = client.get("/openapi.json")
    schema = res.json()
    tag_names = {t["name"] for t in schema.get("tags", [])}

    expected_tags = {"Health", "Auth", "Claims", "QA", "Analytics", "Providers", "Payers", "Issues"}
    assert expected_tags.issubset(tag_names)


def test_docs_and_redoc_endpoints():
    """Verify /docs (Swagger) and /redoc HTML documentation pages render 200."""
    app = create_app()
    client = TestClient(app)

    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    assert "swagger-ui" in res_docs.text.lower() or "html" in res_docs.text.lower()

    res_redoc = client.get("/redoc")
    assert res_redoc.status_code == 200
    assert "redoc" in res_redoc.text.lower() or "html" in res_redoc.text.lower()

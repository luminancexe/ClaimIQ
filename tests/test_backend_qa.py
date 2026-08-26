"""Tests for ClaimIQ Phase 7 QA endpoints."""

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.dependencies import get_db
from backend.services.auth import create_access_token


def _get_auth_headers():
    token = create_access_token("usr-qa-001", "qa_reviewer", "QA_REVIEWER")
    return {"Authorization": f"Bearer {token}"}


def test_list_all_67_qa_rules():
    """Verify GET /api/v1/qa/rules returns all 67 rules from registry."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/qa/rules", headers=_get_auth_headers())
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) == 67
    assert all("rule_code" in r for r in rules)
    assert any(r["rule_code"] == "R-E001" for r in rules)
    assert any(r["rule_code"] == "R-E067" for r in rules)


def test_filter_qa_rules_by_category():
    """Verify category filtering returns matching subset of rules."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/qa/rules?category=FINANCIAL", headers=_get_auth_headers())
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) > 0
    assert all(r["category_code"] == "FINANCIAL" for r in rules)


def test_filter_qa_rules_by_dimension():
    """Verify dimension filtering returns matching subset of rules."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/qa/rules?dimension=validity", headers=_get_auth_headers())
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) > 0
    assert all(r["dimension_code"].lower() == "validity" for r in rules)


def test_get_qa_rule_detail_by_code():
    """Verify lookup of specific QA rule by rule_code."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/qa/rules/R-E001", headers=_get_auth_headers())
    assert res.status_code == 200
    rule = res.json()
    assert rule["rule_code"] == "R-E001"
    assert rule["default_severity_code"] in ("Critical", "High", "Medium", "Low")


def test_get_qa_rule_not_found():
    """Verify nonexistent rule returns 404."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/qa/rules/R-NONEXISTENT", headers=_get_auth_headers())
    assert res.status_code == 404


def test_get_dq_scores_default():
    """Verify GET /api/v1/qa/scores returns clean baseline scores when DB is offline."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    res = client.get("/api/v1/qa/scores", headers=_get_auth_headers())
    assert res.status_code == 200
    scores = res.json()
    assert scores["overall_dq_score"] == 100.0
    assert "dimension_scores" in scores
    assert "severity_breakdown" in scores

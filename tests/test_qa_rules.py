"""Unit tests for QA rule definitions, SQL query construction, and metadata integrity."""

import pytest
from qa.registry import ALL_RULE_DEFINITIONS
from qa.validators import audit_rule_registry_integrity


def test_rule_registry_integrity_audit():
    audit = audit_rule_registry_integrity()
    assert audit["status"] == "PASS"
    assert audit["total_rules"] == 67
    assert len(audit["errors"]) == 0


def test_rule_sql_query_validity():
    for r in ALL_RULE_DEFINITIONS:
        sql = r.sql_logic.strip()
        assert sql.upper().startswith("SELECT"), f"Rule {r.rule_code} SQL does not start with SELECT"
        assert "FROM" in sql.upper(), f"Rule {r.rule_code} SQL does not contain FROM"
        assert r.target_table in sql, f"Rule {r.rule_code} target table '{r.target_table}' not referenced in query"


def test_rule_detection_methods():
    for r in ALL_RULE_DEFINITIONS:
        assert r.detection_method in ("SQL_SET", "SQL_AGGREGATE", "PYTHON_VALIDATION", "COMPOSITE_EVALUATOR")
        if r.rule_code == "R-E061":
            assert r.detection_method == "PYTHON_VALIDATION"
        else:
            assert r.detection_method == "SQL_SET"

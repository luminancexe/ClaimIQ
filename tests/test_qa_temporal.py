"""Unit tests for temporal QA rule logic and chronological sequence detection."""

import pytest
from qa.registry import get_rule


def test_temporal_rules_catalog():
    temp_codes = [f"R-E{i:03d}" for i in range(34, 43)]
    for code in temp_codes:
        r = get_rule(code)
        assert r.category_code == "TEMPORAL"
        assert r.dimension_code == "Temporal"
        assert r.default_severity_code in ("Critical", "High", "Medium")


def test_dos_after_submission_rule():
    r = get_rule("R-E034")
    assert "e.date_of_service > c.submission_date" in r.sql_logic
    assert r.target_table == "encounters"
    assert r.target_column == "date_of_service"


def test_submission_preceding_dob_rule():
    r = get_rule("R-E042")
    assert "c.submission_date < p.date_of_birth" in r.sql_logic
    assert r.target_table == "claims"
    assert r.default_severity_code == "Critical"

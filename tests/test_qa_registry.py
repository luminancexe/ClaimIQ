"""Unit tests for QA Rule Registry, taxonomy indexing, and dimension mapping."""

import pytest
from qa.models import QARuleDefinition
from qa.registry import (
    QA_RULE_REGISTRY,
    ANOMALY_TO_RULE_MAP,
    get_rule,
    get_rule_by_anomaly,
    get_rules_by_category,
    get_rules_by_dimension,
    list_all_rules,
)


def test_qa_registry_complete_inventory():
    # Exactly 67 rules registered
    assert len(QA_RULE_REGISTRY) == 67
    for i in range(1, 68):
        rule_code = f"R-E{i:03d}"
        assert rule_code in QA_RULE_REGISTRY, f"Missing expected QA rule {rule_code}"


def test_anomaly_to_rule_coverage():
    # Every anomaly code E001 to E067 maps to a rule
    for i in range(1, 68):
        anomaly_code = f"E{i:03d}"
        rule = get_rule_by_anomaly(anomaly_code)
        assert rule is not None, f"Anomaly {anomaly_code} does not map to any QA rule"
        assert anomaly_code in rule.anomaly_codes


def test_rule_categories_and_dimensions():
    categories = {r.category_code for r in QA_RULE_REGISTRY.values()}
    assert len(categories) == 7
    expected_categories = {
        "COMPLETENESS", "VALIDITY", "UNIQUENESS", "FINANCIAL",
        "TEMPORAL", "REFERENTIAL", "BUSINESS_LOGIC"
    }
    assert categories == expected_categories

    dimensions = {r.dimension_code for r in QA_RULE_REGISTRY.values()}
    assert len(dimensions) == 7
    expected_dimensions = {
        "Referential Integrity", "Financial", "Completeness",
        "Validity", "Uniqueness", "Temporal", "Accuracy"
    }
    assert dimensions == expected_dimensions


def test_rule_lookups_and_filters():
    r_fin = get_rule("R-E023")
    assert r_fin.rule_code == "R-E023"
    assert r_fin.dimension_code == "Financial"
    assert r_fin.default_severity_code == "Critical"

    # Lookup by anomaly code directly
    r_by_anom = get_rule("E023")
    assert r_by_anom.rule_code == "R-E023"

    fin_rules = get_rules_by_category("FINANCIAL")
    assert len(fin_rules) == 11  # R-E023 to R-E033

    temp_rules = get_rules_by_dimension("Temporal")
    assert len(temp_rules) == 9   # R-E034 to R-E042

    all_rules = list_all_rules()
    assert len(all_rules) == 67

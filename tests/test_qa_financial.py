"""Unit tests for financial QA rule logic and reconciliation equations."""

from decimal import Decimal
import pytest
from qa.registry import get_rule


def test_financial_rules_catalog():
    fin_codes = [f"R-E{i:03d}" for i in range(23, 34)]
    for code in fin_codes:
        r = get_rule(code)
        assert r.category_code == "FINANCIAL"
        assert r.dimension_code == "Financial"
        assert r.default_severity_code in ("Critical", "High", "Medium")


def test_overpayment_rule_logic():
    r = get_rule("R-E023")
    assert "p.paid_amount > c.total_billed_amount" in r.sql_logic
    assert r.target_table == "payments"
    assert r.target_column == "paid_amount"
    assert r.default_severity_code == "Critical"


def test_reconciliation_variance_rule_logic():
    r = get_rule("R-E029")
    assert "r.variance_amount != 0.00" in r.sql_logic
    assert r.target_table == "reconciliations"
    assert r.target_column == "variance_amount"
    assert r.default_severity_code == "Critical"


def test_claim_line_sum_rule_logic():
    r = get_rule("R-E030")
    assert "HAVING c.total_billed_amount != COALESCE(SUM(cl.line_billed_amount), 0.00)" in r.sql_logic
    assert r.target_table == "claims"
    assert r.target_column == "total_billed_amount"

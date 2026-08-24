"""Unit tests for lifecycle and FSM state transition QA rules."""

import pytest
from qa.registry import get_rule


def test_lifecycle_rules_catalog():
    life_codes = [f"R-E{i:03d}" for i in range(43, 51)]
    for code in life_codes:
        r = get_rule(code)
        assert r.category_code == "BUSINESS_LOGIC"
        assert r.dimension_code == "Accuracy"


def test_illegal_state_transition_rule():
    r = get_rule("R-E043")
    assert "h.previous_status_code = 'Denied'" in r.sql_logic
    assert "h.new_status_code = 'Paid'" in r.sql_logic
    assert r.target_table == "claim_status_history"


def test_denied_claim_with_payment_rule():
    r = get_rule("R-E045")
    assert "c.current_status_code = 'Denied'" in r.sql_logic
    assert "p.paid_amount > 0.00" in r.sql_logic
    assert r.target_table == "claims"

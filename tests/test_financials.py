"""Unit tests for Decimal fixed-point financial calculations and reconciliation invariants."""

from decimal import Decimal
import pytest
from generator.random_state import GeneratorRandomState
from generator.financials import (
    quantize_currency,
    calculate_line_billed,
    sum_claim_lines,
    calculate_clean_financial_breakdown,
)


def test_quantize_currency():
    assert quantize_currency(123.456) == Decimal("123.46")
    assert quantize_currency("100.50") == Decimal("100.50")
    assert quantize_currency(Decimal("50")) == Decimal("50.00")


def test_line_billed_calculation():
    units = Decimal("2.00")
    unit_price = Decimal("145.75")
    line_billed = calculate_line_billed(units, unit_price)
    assert line_billed == Decimal("291.50")


def test_sum_claim_lines():
    lines = [Decimal("100.25"), Decimal("250.50"), Decimal("75.25")]
    total = sum_claim_lines(lines)
    assert total == Decimal("426.00")


def test_clean_financial_breakdown_invariants():
    rng = GeneratorRandomState(42)

    for _ in range(100):
        billed = quantize_currency(rng.uniform(100.0, 5000.0))

        # Test Paid
        paid_res = calculate_clean_financial_breakdown(billed, "Paid", rng)
        assert paid_res["total_paid"] > Decimal("0.00")
        assert paid_res["total_paid"] + paid_res["total_adjusted"] + paid_res["total_patient_resp"] == billed
        assert paid_res["variance_amount"] == Decimal("0.00")
        assert paid_res["reconciliation_status"] == "BALANCED"

        # Test Partially Paid
        part_res = calculate_clean_financial_breakdown(billed, "Partially Paid", rng)
        assert part_res["total_paid"] < billed
        assert part_res["total_paid"] + part_res["total_adjusted"] + part_res["total_patient_resp"] == billed
        assert part_res["variance_amount"] == Decimal("0.00")
        assert part_res["reconciliation_status"] == "BALANCED"
        assert len(part_res["adjustments"]) >= 1

        # Test Denied
        den_res = calculate_clean_financial_breakdown(billed, "Denied", rng)
        assert den_res["total_paid"] == Decimal("0.00")
        assert den_res["total_paid"] + den_res["total_adjusted"] + den_res["total_patient_resp"] == billed
        assert den_res["variance_amount"] == Decimal("0.00")
        assert den_res["denial"] is not None
        assert den_res["reconciliation_status"] == "BALANCED"

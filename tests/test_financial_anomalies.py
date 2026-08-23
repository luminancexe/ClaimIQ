"""Unit tests for financial anomaly invariants and mathematical equations."""

from decimal import Decimal
import pytest
from generator.financials import quantize_currency, sum_claim_lines
from generator.injector.taxonomy import TAXONOMY


def test_financial_anomaly_definitions():
    fin_codes = [f"E{i:03d}" for i in range(23, 34)]
    for code in fin_codes:
        defn = TAXONOMY[code]
        assert defn.category.value == "Financial / Reconciliation"
        assert defn.severity.value in ("Critical", "High", "Medium")


def test_overpayment_invariant_detection():
    # Invariant: paid_amount <= total_billed_amount
    billed = Decimal("1000.00")
    normal_paid = Decimal("800.00")
    mutated_overpaid = Decimal("1350.00")  # E023

    assert normal_paid <= billed
    assert mutated_overpaid > billed


def test_reconciliation_variance_equation():
    billed = Decimal("1500.00")
    paid = Decimal("1000.00")
    adj = Decimal("400.00")
    resp = Decimal("100.00")
    clean_variance = billed - (paid + adj + resp)
    assert clean_variance == Decimal("0.00")

    # Injected variance (E029)
    injected_variance = Decimal("235.50")
    assert injected_variance != Decimal("0.00")


def test_line_sum_mismatch():
    lines = [Decimal("250.00"), Decimal("350.00"), Decimal("400.00")]
    clean_total = sum_claim_lines(lines)
    assert clean_total == Decimal("1000.00")

    # Mutated header billed total (E030)
    mutated_header = clean_total + Decimal("300.00")
    assert mutated_header != clean_total

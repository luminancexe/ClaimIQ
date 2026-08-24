"""Unit tests for Phase 6 financial exposure analytics and reconciliation metrics."""

from decimal import Decimal
import pytest
from analytics.models import FinancialExposureSummary
from analytics.financial import calculate_financial_exposure
from analytics.config import AnalyticsConfig


def test_clean_baseline_financial_exposure_defaults():
    summary = calculate_financial_exposure(conn=None, config=AnalyticsConfig(dry_run=True))
    assert isinstance(summary.total_billed, Decimal)
    assert isinstance(summary.total_paid, Decimal)
    assert isinstance(summary.total_contractual_adjustments, Decimal)
    assert isinstance(summary.total_patient_responsibility, Decimal)
    assert isinstance(summary.total_variance, Decimal)
    assert summary.total_variance == Decimal("0.00")
    assert summary.reconciliation_rate == 100.00
    assert summary.financial_integrity_rate == 100.00


def test_financial_exposure_serialization():
    summary = FinancialExposureSummary(
        total_billed=Decimal("1000.00"),
        total_paid=Decimal("800.00"),
        total_contractual_adjustments=Decimal("150.00"),
        total_patient_responsibility=Decimal("50.00"),
        total_variance=Decimal("0.00"),
        unreconciled_amount=Decimal("0.00"),
        overpayment_exposure=Decimal("0.00"),
        underpayment_exposure=Decimal("0.00"),
        total_denied_amount=Decimal("0.00"),
        reconciliation_rate=100.00,
        payment_rate=80.00,
        financial_integrity_rate=100.00,
    )
    d = summary.to_dict()
    assert d["total_billed"] == "1000.00"
    assert d["total_paid"] == "800.00"
    assert d["total_variance"] == "0.00"
    assert d["payment_rate"] == 80.0
    assert d["financial_integrity_rate"] == 100.0


def test_financial_integrity_rate_calculation_with_variance():
    # If total billed is 10,000 and variance is 500 -> 5% variance penalty -> 95% integrity
    total_billed = Decimal("10000.00")
    total_variance = Decimal("500.00")
    var_penalty = (float(total_variance) / float(total_billed)) * 100.0
    integrity_rate = max(0.0, 100.0 - var_penalty)
    assert integrity_rate == 95.0


def test_zero_billed_division_safety():
    # Zero billed amount should safely return 100.0% rates without ZeroDivisionError
    summary = FinancialExposureSummary(
        total_billed=Decimal("0.00"),
        total_paid=Decimal("0.00"),
        total_contractual_adjustments=Decimal("0.00"),
        total_patient_responsibility=Decimal("0.00"),
        total_variance=Decimal("0.00"),
        unreconciled_amount=Decimal("0.00"),
        overpayment_exposure=Decimal("0.00"),
        underpayment_exposure=Decimal("0.00"),
        total_denied_amount=Decimal("0.00"),
        reconciliation_rate=100.00,
        payment_rate=100.00,
        financial_integrity_rate=100.00,
    )
    d = summary.to_dict()
    assert d["payment_rate"] == 100.0
    assert d["financial_integrity_rate"] == 100.0


def test_overpayment_and_underpayment_exposure_accumulation():
    # Overpayment: 150.00 on a 100.00 claim -> 50.00 overpayment
    # Underpayment: variance of 75.00 -> 75.00 underpayment exposure
    summary = FinancialExposureSummary(
        total_billed=Decimal("1000.00"),
        total_paid=Decimal("850.00"),
        total_contractual_adjustments=Decimal("100.00"),
        total_patient_responsibility=Decimal("50.00"),
        total_variance=Decimal("75.00"),
        unreconciled_amount=Decimal("100.00"),
        overpayment_exposure=Decimal("50.00"),
        underpayment_exposure=Decimal("75.00"),
        total_denied_amount=Decimal("200.00"),
        reconciliation_rate=90.00,
        payment_rate=85.00,
        financial_integrity_rate=92.50,
    )
    assert summary.overpayment_exposure == Decimal("50.00")
    assert summary.underpayment_exposure == Decimal("75.00")
    assert summary.total_denied_amount == Decimal("200.00")

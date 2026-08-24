"""Unit tests for Phase 6 operational and QA KPI rollups."""

from decimal import Decimal
import pytest
from analytics.models import ClaimsKPIOverview, PaymentKPIOverview, DenialKPIOverview, QAKPIOverview, KPIOverview
from analytics.kpis import calculate_kpi_overview, calculate_claims_kpis, calculate_payment_kpis, calculate_denial_kpis, calculate_qa_kpis


def test_kpi_overview_simulation():
    kpis = calculate_kpi_overview(conn=None)
    assert kpis.claims.total_claims == 1000
    assert kpis.claims.adjudication_rate == 95.0
    assert kpis.payments.total_payments_count == 850
    assert kpis.payments.average_payment_amount == Decimal("235.29")
    assert kpis.denials.total_denials == 100
    assert kpis.qa.clean_record_rate == 100.0


def test_claims_kpi_serialization():
    claims_kpi = ClaimsKPIOverview(
        total_claims=500,
        status_distribution={"Paid": 400, "Denied": 50, "Submitted": 50},
        adjudicated_claims=450,
        adjudication_rate=90.00,
        reconciled_claims=450,
    )
    d = claims_kpi.to_dict()
    assert d["total_claims"] == 500
    assert d["adjudication_rate"] == 90.0
    assert d["reconciled_claims"] == 450
    assert d["status_distribution"]["Paid"] == 400


def test_defect_density_and_clean_record_rate():
    total_claims = 1000
    total_issues = 25
    defective_claims = 20
    clean_claims = total_claims - defective_claims
    clean_rate = (clean_claims / total_claims) * 100.0
    density = total_issues / total_claims

    assert clean_rate == 98.0
    assert density == 0.025


def test_payment_kpis_serialization():
    pmt_kpi = PaymentKPIOverview(
        total_payments_count=100,
        total_paid_amount=Decimal("25000.00"),
        average_payment_amount=Decimal("250.00"),
        zero_payment_count=2,
        average_payment_turnaround_days=3.5,
    )
    d = pmt_kpi.to_dict()
    assert d["total_payments_count"] == 100
    assert d["total_paid_amount"] == "25000.00"
    assert d["average_payment_turnaround_days"] == 3.5


def test_denial_kpis_serialization():
    den_kpi = DenialKPIOverview(
        total_denials=20,
        denial_rate=5.0,
        appealable_rate=90.0,
        top_denial_reasons=[{"denial_code": "CO-16", "count": 12}],
        denial_financial_exposure=Decimal("6000.00"),
    )
    d = den_kpi.to_dict()
    assert d["total_denials"] == 20
    assert d["denial_rate"] == 5.0
    assert d["appealable_rate"] == 90.0
    assert d["denial_financial_exposure"] == "6000.00"

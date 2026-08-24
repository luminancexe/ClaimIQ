"""Unit tests for Analytics Engine determinism and repeatable calculation."""

import pytest
from analytics.config import AnalyticsConfig
from analytics.engine import AnalyticsExecutionEngine
from analytics.financial import calculate_financial_exposure
from analytics.kpis import calculate_kpi_overview
from analytics.scorecards import generate_provider_scorecards, generate_payer_scorecards
from analytics.trends import calculate_dq_trends
from analytics.root_cause import calculate_root_cause_distribution
from analytics.recurrence import calculate_recurrence_patterns


def test_financial_determinism():
    res1 = calculate_financial_exposure(conn=None)
    res2 = calculate_financial_exposure(conn=None)
    assert res1.total_billed == res2.total_billed
    assert res1.total_paid == res2.total_paid
    assert res1.reconciliation_rate == res2.reconciliation_rate
    assert res1.financial_integrity_rate == res2.financial_integrity_rate


def test_kpi_determinism():
    kpi1 = calculate_kpi_overview(conn=None)
    kpi2 = calculate_kpi_overview(conn=None)
    assert kpi1.claims.total_claims == kpi2.claims.total_claims
    assert kpi1.payments.total_paid_amount == kpi2.payments.total_paid_amount
    assert kpi1.qa.clean_record_rate == kpi2.qa.clean_record_rate


def test_scorecard_and_pareto_determinism():
    sc1 = generate_provider_scorecards(conn=None)
    sc2 = generate_provider_scorecards(conn=None)
    assert [s.provider_id for s in sc1] == [s.provider_id for s in sc2]

    rc1 = calculate_root_cause_distribution(conn=None)
    rc2 = calculate_root_cause_distribution(conn=None)
    assert [i.anomaly_code for i in rc1.items] == [i.anomaly_code for i in rc2.items]
    assert rc1.pareto_cutoff_index == rc2.pareto_cutoff_index


def test_engine_determinism():
    cfg1 = AnalyticsConfig(report_type="all", dry_run=True)
    engine1 = AnalyticsExecutionEngine(cfg1)
    rep1 = engine1.execute()

    cfg2 = AnalyticsConfig(report_type="all", dry_run=True)
    engine2 = AnalyticsExecutionEngine(cfg2)
    rep2 = engine2.execute()

    assert rep1.financial.total_billed == rep2.financial.total_billed
    assert rep1.kpis.claims.total_claims == rep2.kpis.claims.total_claims
    assert len(rep1.provider_scorecards) == len(rep2.provider_scorecards)
    assert rep1.dq_trends.rolling_average_score == rep2.dq_trends.rolling_average_score

"""Unit tests for the AnalyticsExecutionEngine orchestrator and selective report generation."""

import pytest
from analytics.config import AnalyticsConfig
from analytics.engine import AnalyticsExecutionEngine


def test_engine_selective_financial_report():
    cfg = AnalyticsConfig(report_type="financial", dry_run=True)
    engine = AnalyticsExecutionEngine(cfg)
    report = engine.execute()

    assert report.financial is not None
    assert report.kpis is None
    assert report.provider_scorecards is None
    assert report.telemetry.status == "SUCCESS"


def test_engine_selective_kpis_report():
    cfg = AnalyticsConfig(report_type="kpis", dry_run=True)
    engine = AnalyticsExecutionEngine(cfg)
    report = engine.execute()

    assert report.kpis is not None
    assert report.financial is None
    assert report.kpis.claims.total_claims == 1000


def test_engine_selective_provider_report():
    cfg = AnalyticsConfig(report_type="provider", dry_run=True)
    engine = AnalyticsExecutionEngine(cfg)
    report = engine.execute()

    assert report.provider_scorecards is not None
    assert len(report.provider_scorecards) > 0


def test_engine_full_report_generation():
    cfg = AnalyticsConfig(report_type="all", dry_run=True)
    engine = AnalyticsExecutionEngine(cfg)
    report = engine.execute()

    assert report.financial is not None
    assert report.kpis is not None
    assert report.provider_scorecards is not None
    assert report.payer_scorecards is not None
    assert report.dq_trends is not None
    assert report.root_cause is not None
    assert report.recurrence is not None
    assert report.telemetry.report_type == "all"

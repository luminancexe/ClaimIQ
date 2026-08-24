"""Integration tests for Phase 6 Analytics CLI execution, JSON export, and end-to-end reporting."""

import json
import tempfile
import pytest
from analytics.config import AnalyticsConfig
from analytics.engine import AnalyticsExecutionEngine


def test_analytics_cli_report_export_to_json():
    cfg = AnalyticsConfig(report_type="all", dry_run=True)
    engine = AnalyticsExecutionEngine(cfg)
    report = engine.execute()
    report_dict = report.to_dict()

    assert report_dict["report_id"].startswith("ANL-REP-")
    assert report_dict["financial"]["total_variance"] == "0.00"
    assert "provider_scorecards" in report_dict
    assert "payer_scorecards" in report_dict
    assert "dq_trends" in report_dict
    assert "root_cause" in report_dict
    assert "recurrence" in report_dict

    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
        json.dump(report_dict, tmp)
        tmp.seek(0)
        loaded = json.load(tmp)
        assert loaded["report_id"] == report_dict["report_id"]
        assert loaded["financial"]["payment_rate"] == 80.0


def test_overview_report_structure():
    cfg = AnalyticsConfig(report_type="overview", dry_run=True)
    engine = AnalyticsExecutionEngine(cfg)
    report = engine.execute()

    assert report.financial is not None
    assert report.kpis is not None
    assert report.root_cause is not None
    assert report.provider_scorecards is None
    assert report.payer_scorecards is None

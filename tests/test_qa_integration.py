"""Integration tests for the ClaimIQ Phase 5 QA execution engine and telemetry."""

import pytest
from qa.config import QAConfig
from qa.engine import QAExecutionEngine


def test_dry_run_engine_execution():
    cfg = QAConfig(dry_run=True, batch_identifier="BATCH-TEST-001")
    engine = QAExecutionEngine(cfg)
    result = engine.execute()

    assert result["status"] == "DRY_RUN_COMPLETE"
    assert result["batch_identifier"] == "BATCH-TEST-001"
    assert result["rules_evaluated"] == 67
    assert result["overall_dq_score"] == 100.0
    assert result["total_issues_detected"] == 0
    assert "dq_summary" in result
    assert len(result["dq_summary"]["dimension_scores"]) == 7


def test_filtered_category_execution():
    cfg = QAConfig(dry_run=True, category_filter="FINANCIAL")
    engine = QAExecutionEngine(cfg)
    result = engine.execute()

    assert result["status"] == "DRY_RUN_COMPLETE"
    assert result["rules_evaluated"] == 11

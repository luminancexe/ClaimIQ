"""Unit tests for QA engine determinism and reproducible evaluation."""

import pytest
from qa.config import QAConfig
from qa.engine import QAExecutionEngine
from qa.models import QARunTelemetry, QADetectionRecord
from qa.scoring import calculate_dq_score
from qa.ground_truth import evaluate_ground_truth_accuracy
from generator.injector.models import GroundTruthRecord


def test_rule_resolution_determinism():
    cfg1 = QAConfig(category_filter="FINANCIAL")
    engine1 = QAExecutionEngine(cfg1)
    rules1 = [r.rule_code for r in engine1.get_effective_rules()]

    cfg2 = QAConfig(category_filter="FINANCIAL")
    engine2 = QAExecutionEngine(cfg2)
    rules2 = [r.rule_code for r in engine2.get_effective_rules()]

    assert rules1 == rules2
    assert len(rules1) == 11


def test_scoring_determinism():
    telemetry = [
        QARunTelemetry(rule_code="R-E023", records_evaluated=500, issues_detected=3, execution_duration_ms=10),
        QARunTelemetry(rule_code="R-E034", records_evaluated=500, issues_detected=2, execution_duration_ms=10),
    ]
    detections = [
        QADetectionRecord(rule_code="R-E023", anomaly_code="E023", target_table="payments", target_record_id=1, severity_code="Critical", dimension_code="Financial"),
        QADetectionRecord(rule_code="R-E023", anomaly_code="E023", target_table="payments", target_record_id=2, severity_code="Critical", dimension_code="Financial"),
        QADetectionRecord(rule_code="R-E023", anomaly_code="E023", target_table="payments", target_record_id=3, severity_code="Critical", dimension_code="Financial"),
        QADetectionRecord(rule_code="R-E034", anomaly_code="E034", target_table="encounters", target_record_id=10, severity_code="High", dimension_code="Temporal"),
        QADetectionRecord(rule_code="R-E034", anomaly_code="E034", target_table="encounters", target_record_id=11, severity_code="High", dimension_code="Temporal"),
    ]

    score1 = calculate_dq_score(telemetry, detections)
    score2 = calculate_dq_score(telemetry, detections)

    assert score1.overall_dq_score == score2.overall_dq_score
    assert score1.total_issues_detected == score2.total_issues_detected
    assert score1.dimension_scores["Financial"].weighted_score == score2.dimension_scores["Financial"].weighted_score

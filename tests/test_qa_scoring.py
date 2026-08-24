"""Unit tests for 7-dimension Data Quality scoring formulas and weights."""

import pytest
from qa.models import QADetectionRecord, QARunTelemetry
from qa.scoring import calculate_dq_score, DIMENSION_METADATA


def test_dimension_weights_sum_to_one():
    total_weight = sum(meta["weight"] for meta in DIMENSION_METADATA.values())
    assert pytest.approx(total_weight, 0.001) == 1.00


def test_clean_telemetry_scores_100():
    telemetry = [
        QARunTelemetry(rule_code="R-E001", records_evaluated=100, issues_detected=0, execution_duration_ms=5),
        QARunTelemetry(rule_code="R-E023", records_evaluated=100, issues_detected=0, execution_duration_ms=5),
        QARunTelemetry(rule_code="R-E034", records_evaluated=100, issues_detected=0, execution_duration_ms=5),
    ]
    detections = []

    res = calculate_dq_score(telemetry, detections)
    assert res.overall_dq_score == 100.00
    assert res.total_issues_detected == 0
    for dim_s in res.dimension_scores.values():
        assert dim_s.raw_score == 100.00


def test_severity_penalties_impact():
    telemetry = [
        QARunTelemetry(rule_code="R-E023", records_evaluated=100, issues_detected=5, execution_duration_ms=5),
    ]
    crit_detections = [
        QADetectionRecord(
            rule_code="R-E023",
            anomaly_code="E023",
            target_table="payments",
            target_record_id=i,
            severity_code="Critical",
            dimension_code="Financial",
        )
        for i in range(5)
    ]

    res = calculate_dq_score(telemetry, crit_detections)
    fin_score = res.dimension_scores["Financial"].raw_score
    assert fin_score < 100.0
    assert res.overall_dq_score < 100.0

"""Unit tests for Ground Truth evaluation, TP/FP/FN classification, and Precision/Recall/F1 metrics."""

import pytest
from generator.injector.models import GroundTruthRecord
from qa.models import QADetectionRecord
from qa.ground_truth import evaluate_ground_truth_accuracy


def test_perfect_ground_truth_matching():
    gt_records = [
        GroundTruthRecord(
            anomaly_code="E023",
            category_name="Financial / Reconciliation",
            severity_code="Critical",
            target_table="payments",
            target_record_id=101,
            target_column="paid_amount",
            original_value="500.00",
            mutated_value="850.00",
            injection_profile="moderate",
            injection_seed=42,
            description="Overpayment",
            expected_rule_category="Financial",
        ),
        GroundTruthRecord(
            anomaly_code="E034",
            category_name="Temporal",
            severity_code="High",
            target_table="encounters",
            target_record_id=202,
            target_column="date_of_service",
            original_value="2025-05-01",
            mutated_value="2025-05-25",
            injection_profile="moderate",
            injection_seed=42,
            description="DOS after submission",
            expected_rule_category="Temporal",
        ),
    ]

    detections = [
        QADetectionRecord(
            rule_code="R-E023",
            anomaly_code="E023",
            target_table="payments",
            target_record_id=101,
            target_column="paid_amount",
            detected_value="850.00",
            severity_code="Critical",
            dimension_code="Financial",
        ),
        QADetectionRecord(
            rule_code="R-E034",
            anomaly_code="E034",
            target_table="encounters",
            target_record_id=202,
            target_column="date_of_service",
            detected_value="2025-05-25",
            severity_code="High",
            dimension_code="Temporal",
        ),
    ]

    res = evaluate_ground_truth_accuracy(detections=detections, ground_truth_records=gt_records)
    assert res.total_ground_truth_anomalies == 2
    assert res.total_qa_detections == 2
    assert res.true_positives == 2
    assert res.false_positives == 0
    assert res.false_negatives == 0
    assert res.precision == 1.0
    assert res.recall == 1.0
    assert res.f1_score == 1.0


def test_mixed_precision_and_recall_calculation():
    # 2 Ground Truth records
    gt_records = [
        GroundTruthRecord(
            anomaly_code="E001",
            category_name="Completeness",
            severity_code="Low",
            target_table="patients",
            target_record_id=1,
            target_column="address_state",
            original_value="CA",
            mutated_value="",
            injection_profile="test",
            injection_seed=1,
            description="Missing state",
            expected_rule_category="Completeness",
        ),
        GroundTruthRecord(
            anomaly_code="E002",
            category_name="Completeness",
            severity_code="Medium",
            target_table="providers",
            target_record_id=2,
            target_column="facility_id",
            original_value="10",
            mutated_value="NULL",
            injection_profile="test",
            injection_seed=1,
            description="Missing facility",
            expected_rule_category="Completeness",
        ),
    ]

    # Detections: E001 (TP), E099 (FP). Missing E002 (FN).
    detections = [
        QADetectionRecord(
            rule_code="R-E001",
            anomaly_code="E001",
            target_table="patients",
            target_record_id=1,
            target_column="address_state",
        ),
        QADetectionRecord(
            rule_code="R-E099",
            anomaly_code="E099",
            target_table="patients",
            target_record_id=99,
            target_column="extra_field",
        ),
    ]

    res = evaluate_ground_truth_accuracy(detections=detections, ground_truth_records=gt_records)
    assert res.true_positives == 1
    assert res.false_positives == 1
    assert res.false_negatives == 1
    assert res.precision == 0.5
    assert res.recall == 0.5
    assert res.f1_score == 0.5


def test_zero_anomalies_clean_dataset():
    res = evaluate_ground_truth_accuracy(detections=[], ground_truth_records=[])
    assert res.true_positives == 0
    assert res.false_positives == 0
    assert res.false_negatives == 0
    assert res.precision == 1.0
    assert res.recall == 1.0
    assert res.f1_score == 1.0

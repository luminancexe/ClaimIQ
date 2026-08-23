"""Unit tests for GroundTruthRecord modeling and JSON serialization."""

import os
import tempfile
import pytest
from generator.injector.models import GroundTruthRecord
from generator.injector.ground_truth import (
    export_ground_truth_to_json,
    import_ground_truth_from_json,
)


def test_ground_truth_record_serialization():
    rec = GroundTruthRecord(
        anomaly_code="E023",
        category_name="Financial / Reconciliation",
        severity_code="Critical",
        target_table="payments",
        target_record_id=42,
        target_business_reference="PMT-2025-0000042",
        target_column="paid_amount",
        original_value="800.00",
        mutated_value="1350.00",
        injection_profile="moderate",
        injection_seed=42,
        description="Payment exceeds total billed amount",
        expected_rule_category="Financial Integrity",
    )

    data = rec.to_dict()
    assert data["anomaly_code"] == "E023"
    assert data["target_record_id"] == 42
    assert data["original_value"] == "800.00"
    assert data["mutated_value"] == "1350.00"

    reconstructed = GroundTruthRecord.from_dict(data)
    assert reconstructed.anomaly_code == rec.anomaly_code
    assert reconstructed.target_record_id == rec.target_record_id
    assert reconstructed.mutated_value == rec.mutated_value


def test_ground_truth_json_export_and_import():
    records = [
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
            injection_seed=123,
            description="Missing state",
            expected_rule_category="Completeness",
        ),
        GroundTruthRecord(
            anomaly_code="E034",
            category_name="Temporal",
            severity_code="High",
            target_table="encounters",
            target_record_id=10,
            target_column="date_of_service",
            original_value="2025-05-01",
            mutated_value="2025-05-20",
            injection_profile="test",
            injection_seed=123,
            description="DOS after submission",
            expected_rule_category="Temporal Consistency",
        ),
    ]

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = f.name

    try:
        export_ground_truth_to_json(records, temp_path)
        assert os.path.exists(temp_path)

        loaded = import_ground_truth_from_json(temp_path)
        assert len(loaded) == 2
        assert loaded[0].anomaly_code == "E001"
        assert loaded[1].anomaly_code == "E034"
        assert loaded[1].mutated_value == "2025-05-20"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

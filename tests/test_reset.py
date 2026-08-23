"""Unit tests for mutation reversion and safe reset behaviors."""

import pytest
from generator.injector.ground_truth import TABLE_PK_MAP


def test_table_pk_mapping_coverage():
    # Verify all 16 core domain tables have primary key mappings
    expected_tables = [
        "patients", "facilities", "providers", "payers", "insurance_plans",
        "patient_coverage", "encounters", "encounter_diagnoses", "claims",
        "claim_lines", "claim_status_history", "remittances", "payments",
        "adjustments", "denials", "reconciliations"
    ]
    for tbl in expected_tables:
        assert tbl in TABLE_PK_MAP
        assert TABLE_PK_MAP[tbl].endswith("_id") or TABLE_PK_MAP[tbl] == "history_id"

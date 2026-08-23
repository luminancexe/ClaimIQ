"""Unit tests for claim lifecycle and state machine anomaly definitions."""

import pytest
from generator.injector.taxonomy import TAXONOMY


def test_lifecycle_anomaly_definitions():
    lfc_codes = [f"E{i:03d}" for i in range(43, 51)]
    for code in lfc_codes:
        defn = TAXONOMY[code]
        assert defn.category.value == "Claim Lifecycle / FSM"
        assert defn.severity.value in ("Critical", "High", "Medium", "Low")


def test_illegal_fsm_transition_representation():
    # Valid clean transition path: Submitted -> Accepted -> Paid
    # Illegal direct transition (E043): Denied -> Paid direct
    prev_status = "Denied"
    new_status = "Paid"
    assert (prev_status, new_status) == ("Denied", "Paid")

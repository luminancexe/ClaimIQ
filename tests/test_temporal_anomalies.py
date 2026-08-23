"""Unit tests for temporal anomaly definitions and chronological violations."""

from datetime import date, timedelta
import pytest
from generator.injector.taxonomy import TAXONOMY


def test_temporal_anomaly_definitions():
    temp_codes = [f"E{i:03d}" for i in range(34, 43)]
    for code in temp_codes:
        defn = TAXONOMY[code]
        assert defn.category.value == "Temporal"
        assert defn.severity.value in ("Critical", "High", "Medium")


def test_chronology_violations():
    dos = date(2025, 6, 1)
    sub = date(2025, 6, 15)
    adj = date(2025, 6, 25)
    pmt = date(2025, 6, 28)

    # Clean sequence
    assert dos <= sub <= adj <= pmt

    # E034: DOS after submission
    mutated_dos = sub + timedelta(days=15)
    assert mutated_dos > sub

    # E035: Submission after adjudication
    mutated_sub = adj + timedelta(days=10)
    assert mutated_sub > adj

    # E037: Payment before adjudication
    mutated_pmt = adj - timedelta(days=3)
    assert mutated_pmt < adj

    # E040: Discharge before DOS
    mutated_dis = dos - timedelta(days=2)
    assert mutated_dis < dos

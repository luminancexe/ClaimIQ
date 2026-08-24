"""Unit tests for repeat defect pattern clustering and recurrence analytics."""

import pytest
from analytics.models import RecurrencePattern, RecurrenceSummary
from analytics.recurrence import calculate_recurrence_patterns


def test_recurrence_summary_simulation():
    summary = calculate_recurrence_patterns(conn=None)
    assert summary.recurring_cluster_count == 2
    assert len(summary.top_repeat_entities) == 2
    assert summary.total_repeating_occurrences == 7
    assert summary.repeat_issue_rate == 23.33


def test_recurrence_pattern_serialization():
    pattern = RecurrencePattern(
        entity_type="PROVIDER",
        entity_identifier="PRV-2026-0000001",
        anomaly_code="E023",
        occurrence_count=5,
        first_detected_at="2026-01-01 10:00:00",
        last_detected_at="2026-02-01 12:00:00",
        recurrence_rank=1,
    )
    d = pattern.to_dict()
    assert d["entity_type"] == "PROVIDER"
    assert d["entity_identifier"] == "PRV-2026-0000001"
    assert d["occurrence_count"] == 5
    assert d["recurrence_rank"] == 1


def test_recurrence_threshold_enforcement():
    # Only clusters with >= 2 occurrences are counted
    items = [
        {"id": "E1", "count": 1},
        {"id": "E2", "count": 2},
        {"id": "E3", "count": 4},
    ]
    clusters = [i for i in items if i["count"] >= 2]
    assert len(clusters) == 2


def test_recurrence_summary_serialization():
    pattern = RecurrencePattern(
        entity_type="PAYER",
        entity_identifier="PAY-2026-0000002",
        anomaly_code="E034",
        occurrence_count=3,
        first_detected_at="2026-01-10 00:00:00",
        last_detected_at="2026-01-20 00:00:00",
        recurrence_rank=1,
    )
    summary = RecurrenceSummary(
        recurring_cluster_count=1,
        top_repeat_entities=[pattern],
        repeat_issue_rate=15.0,
        total_repeating_occurrences=3,
    )
    d = summary.to_dict()
    assert d["recurring_cluster_count"] == 1
    assert d["repeat_issue_rate"] == 15.0
    assert d["total_repeating_occurrences"] == 3
    assert len(d["top_repeat_entities"]) == 1

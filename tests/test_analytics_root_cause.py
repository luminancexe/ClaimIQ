"""Unit tests for Pareto 80/20 root cause defect distribution analytics."""

from decimal import Decimal
import pytest
from analytics.models import RootCauseItem, RootCauseDistribution
from analytics.root_cause import calculate_root_cause_distribution


def test_root_cause_distribution_simulation():
    dist = calculate_root_cause_distribution(conn=None)
    assert len(dist.items) == 3
    assert dist.pareto_cutoff_index == 1
    assert "Financial" in dist.primary_defect_driver
    assert dist.total_issues_analyzed == 30
    assert dist.items[0].cumulative_percentage == 50.0
    assert dist.items[1].cumulative_percentage == 83.33
    assert dist.items[2].cumulative_percentage == 100.0


def test_root_cause_serialization():
    item = RootCauseItem(
        anomaly_category="Financial",
        anomaly_code="E023",
        rule_code="R-E023",
        description="Payment Exceeds Total Billed Amount",
        severity_code="Critical",
        dimension_code="Financial",
        issue_count=10,
        percentage_of_total=50.00,
        cumulative_percentage=50.00,
        financial_exposure=Decimal("5000.00"),
    )
    d = item.to_dict()
    assert d["anomaly_code"] == "E023"
    assert d["rule_code"] == "R-E023"
    assert d["financial_exposure"] == "5000.00"


def test_clean_dataset_root_cause():
    # Empty items on zero issues
    dist = RootCauseDistribution(
        items=[],
        pareto_cutoff_index=0,
        primary_defect_driver="None (Clean Dataset)",
        total_issues_analyzed=0,
    )
    assert dist.total_issues_analyzed == 0
    assert len(dist.items) == 0


def test_root_cause_distribution_serialization():
    item = RootCauseItem(
        anomaly_category="Financial",
        anomaly_code="E023",
        rule_code="R-E023",
        description="Payment Exceeds Total Billed Amount",
        severity_code="Critical",
        dimension_code="Financial",
        issue_count=10,
        percentage_of_total=100.00,
        cumulative_percentage=100.00,
        financial_exposure=Decimal("5000.00"),
    )
    dist = RootCauseDistribution(
        items=[item],
        pareto_cutoff_index=0,
        primary_defect_driver="Financial (E023)",
        total_issues_analyzed=10,
    )
    d = dist.to_dict()
    assert d["pareto_cutoff_index"] == 0
    assert d["primary_defect_driver"] == "Financial (E023)"
    assert len(d["items"]) == 1

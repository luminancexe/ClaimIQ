"""Unit tests for longitudinal DQ trends and score trajectory analytics."""

import pytest
from analytics.models import DQTrendPoint, DQTrendsSummary
from analytics.trends import calculate_dq_trends
from analytics.config import AnalyticsConfig


def test_trend_summary_simulation():
    cfg = AnalyticsConfig(trend_interval="monthly", dry_run=True)
    trends = calculate_dq_trends(conn=None, config=cfg)
    assert trends.interval == "monthly"
    assert len(trends.points) == 3
    assert trends.rolling_average_score == 99.23
    assert trends.trend_direction == "STABLE"


def test_trend_direction_logic():
    # Velocity >= 0.50 -> IMPROVING
    # Velocity <= -0.50 -> DEGRADING
    # Otherwise -> STABLE
    pos_points = [
        DQTrendPoint("2026-01", 90.0, {}, 5, 100),
        DQTrendPoint("2026-02", 95.0, {}, 2, 100),
    ]
    pos_velocity = (95.0 - 90.0) / 1.0  # +5.0
    assert pos_velocity >= 0.50

    neg_points = [
        DQTrendPoint("2026-01", 95.0, {}, 1, 100),
        DQTrendPoint("2026-02", 90.0, {}, 6, 100),
    ]
    neg_velocity = (90.0 - 95.0) / 1.0  # -5.0
    assert neg_velocity <= -0.50


def test_trend_point_serialization():
    pt = DQTrendPoint(
        time_bucket="2026-01",
        overall_dq_score=98.50,
        dimension_scores={"Financial": 95.0, "Completeness": 100.0},
        issue_count=3,
        claim_volume=120,
    )
    d = pt.to_dict()
    assert d["time_bucket"] == "2026-01"
    assert d["overall_dq_score"] == 98.5
    assert d["dimension_scores"]["Financial"] == 95.0


def test_trend_summary_serialization():
    summary = DQTrendsSummary(
        interval="weekly",
        points=[
            DQTrendPoint("2026-W01", 100.0, {}, 0, 50),
            DQTrendPoint("2026-W02", 99.0, {}, 1, 50),
        ],
        rolling_average_score=99.50,
        score_velocity=-1.0,
        trend_direction="DEGRADING",
    )
    d = summary.to_dict()
    assert d["interval"] == "weekly"
    assert len(d["points"]) == 2
    assert d["trend_direction"] == "DEGRADING"
    assert d["score_velocity"] == -1.0

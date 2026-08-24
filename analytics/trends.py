"""Longitudinal time-series Data Quality trends and trajectory analytics."""

from typing import Optional, List, Dict, Any
import pymysql
from analytics.config import AnalyticsConfig
from analytics.models import DQTrendPoint, DQTrendsSummary
from analytics.database import execute_analytical_query


def calculate_dq_trends(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> DQTrendsSummary:
    """Calculate longitudinal DQ score trends, score velocities, and dimension trajectories."""
    interval = (config.trend_interval if config else "monthly").lower()

    if interval == "daily":
        date_fmt = "%Y-%m-%d"
    elif interval == "weekly":
        date_fmt = "%Y-W%u"
    else:
        interval = "monthly"
        date_fmt = "%Y-%m"

    if conn is None:
        # Standalone simulated dry-run default
        points = [
            DQTrendPoint(
                time_bucket="2025-01",
                overall_dq_score=100.00,
                dimension_scores={
                    "Referential Integrity": 100.0,
                    "Financial": 100.0,
                    "Completeness": 100.0,
                    "Validity": 100.0,
                    "Uniqueness": 100.0,
                    "Temporal": 100.0,
                    "Accuracy": 100.0,
                },
                issue_count=0,
                claim_volume=150,
            ),
            DQTrendPoint(
                time_bucket="2025-02",
                overall_dq_score=98.50,
                dimension_scores={
                    "Referential Integrity": 100.0,
                    "Financial": 95.0,
                    "Completeness": 100.0,
                    "Validity": 100.0,
                    "Uniqueness": 100.0,
                    "Temporal": 100.0,
                    "Accuracy": 98.0,
                },
                issue_count=2,
                claim_volume=200,
            ),
            DQTrendPoint(
                time_bucket="2025-03",
                overall_dq_score=99.20,
                dimension_scores={
                    "Referential Integrity": 100.0,
                    "Financial": 98.0,
                    "Completeness": 100.0,
                    "Validity": 100.0,
                    "Uniqueness": 100.0,
                    "Temporal": 100.0,
                    "Accuracy": 99.0,
                },
                issue_count=1,
                claim_volume=250,
            ),
        ]
        return DQTrendsSummary(
            interval=interval,
            points=points,
            rolling_average_score=99.23,
            score_velocity=-0.40,
            trend_direction="STABLE",
        )

    # 1. Aggregate claims by time bucket
    claim_sql = f"""
        SELECT 
            DATE_FORMAT(submission_date, '{date_fmt}') AS bucket,
            COUNT(*) AS claim_vol
        FROM claims
        GROUP BY bucket
        ORDER BY bucket ASC
    """
    claim_rows = execute_analytical_query(conn, claim_sql)
    claim_map = {r["bucket"]: r["claim_vol"] for r in claim_rows}

    # 2. Aggregate issues by claim submission date bucket and dimension
    issue_sql = f"""
        SELECT 
            DATE_FORMAT(c.submission_date, '{date_fmt}') AS bucket,
            i.dimension_code,
            COUNT(i.issue_id) AS issue_cnt
        FROM issues i
        JOIN claims c ON i.claim_id = c.claim_id
        GROUP BY bucket, i.dimension_code
    """
    issue_rows = execute_analytical_query(conn, issue_sql)
    
    issue_dim_map: Dict[str, Dict[str, int]] = {}
    issue_tot_map: Dict[str, int] = {}
    for r in issue_rows:
        b = r["bucket"]
        dim = r["dimension_code"]
        cnt = r["issue_cnt"]
        issue_dim_map.setdefault(b, {})[dim] = cnt
        issue_tot_map[b] = issue_tot_map.get(b, 0) + cnt

    all_buckets = sorted(list(claim_map.keys()))
    if not all_buckets:
        all_buckets = ["NO_DATA"]

    points: List[DQTrendPoint] = []
    dim_names = [
        "Referential Integrity", "Financial", "Completeness",
        "Validity", "Uniqueness", "Temporal", "Accuracy"
    ]
    dim_weights = {
        "Referential Integrity": 0.20,
        "Financial": 0.20,
        "Completeness": 0.15,
        "Validity": 0.15,
        "Uniqueness": 0.10,
        "Temporal": 0.10,
        "Accuracy": 0.10,
    }

    for b in all_buckets:
        vol = claim_map.get(b, 0)
        tot_issues = issue_tot_map.get(b, 0)
        dims: Dict[str, float] = {}
        weighted_overall = 0.0

        for dim in dim_names:
            d_iss = issue_dim_map.get(b, {}).get(dim, 0)
            if vol == 0 or d_iss == 0:
                raw_d = 100.0
            else:
                raw_d = max(0.0, 100.0 - (float(d_iss) / float(vol) * 100.0 * 2.0))
            dims[dim] = raw_d
            weighted_overall += raw_d * dim_weights[dim]

        points.append(
            DQTrendPoint(
                time_bucket=b,
                overall_dq_score=weighted_overall,
                dimension_scores=dims,
                issue_count=tot_issues,
                claim_volume=vol,
            )
        )

    # Calculate rolling average and velocity
    if points:
        rolling_avg = sum(p.overall_dq_score for p in points) / float(len(points))
        if len(points) > 1:
            velocity = (points[-1].overall_dq_score - points[0].overall_dq_score) / float(len(points) - 1)
        else:
            velocity = 0.0
    else:
        rolling_avg = 100.0
        velocity = 0.0

    if velocity >= 0.50:
        trend_dir = "IMPROVING"
    elif velocity <= -0.50:
        trend_dir = "DEGRADING"
    else:
        trend_dir = "STABLE"

    return DQTrendsSummary(
        interval=interval,
        points=points,
        rolling_average_score=rolling_avg,
        score_velocity=velocity,
        trend_direction=trend_dir,
    )

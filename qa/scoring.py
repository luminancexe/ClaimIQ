"""Deterministic 7-Dimension Data Quality Scoring Engine for ClaimIQ Phase 5."""

from typing import Dict, List, Any
from qa.models import QADetectionRecord, QARunTelemetry, DQDimensionScore, DQScoreSummary

DIMENSION_METADATA = {
    "Referential Integrity": {"weight": 0.20, "name": "Referential Integrity"},
    "Financial": {"weight": 0.20, "name": "Financial Integrity"},
    "Completeness": {"weight": 0.15, "name": "Completeness"},
    "Validity": {"weight": 0.15, "name": "Validity & Conformance"},
    "Uniqueness": {"weight": 0.10, "name": "Uniqueness"},
    "Temporal": {"weight": 0.10, "name": "Temporal Consistency"},
    "Accuracy": {"weight": 0.10, "name": "Accuracy & State Logic"},
}

SEVERITY_PENALTIES = {
    "Critical": 3.0,
    "High": 2.0,
    "Medium": 1.0,
    "Low": 0.5,
}


def calculate_dq_score(
    telemetry_list: List[QARunTelemetry],
    detections: List[QADetectionRecord],
) -> DQScoreSummary:
    """Calculate deterministic 7-dimension weighted DQ scores and overall score."""
    # Group telemetry by dimension
    from qa.registry import get_rule

    dim_records: Dict[str, int] = {dim: 0 for dim in DIMENSION_METADATA}
    dim_issues: Dict[str, int] = {dim: 0 for dim in DIMENSION_METADATA}
    dim_penalties: Dict[str, float] = {dim: 0.0 for dim in DIMENSION_METADATA}
    severity_counts: Dict[str, int] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    for t in telemetry_list:
        try:
            r = get_rule(t.rule_code)
            dim = r.dimension_code
            if dim in dim_records:
                dim_records[dim] += t.records_evaluated
        except Exception:
            pass

    for d in detections:
        dim = d.dimension_code
        sev = d.severity_code
        if dim in dim_issues:
            dim_issues[dim] += 1
            penalty = SEVERITY_PENALTIES.get(sev, 1.0)
            dim_penalties[dim] += penalty
        if sev in severity_counts:
            severity_counts[sev] += 1

    total_records = sum(t.records_evaluated for t in telemetry_list)
    total_issues = len(detections)

    dimension_scores: Dict[str, DQDimensionScore] = {}
    weighted_total = 0.0

    for dim, meta in DIMENSION_METADATA.items():
        weight = meta["weight"]
        name = meta["name"]
        rec_count = dim_records[dim]
        iss_count = dim_issues[dim]
        penalty_sum = dim_penalties[dim]

        if iss_count == 0 or rec_count == 0:
            raw_score = 100.0
        else:
            # Scale penalty relative to population evaluated
            defect_ratio = penalty_sum / max(rec_count, 1)
            raw_score = max(0.0, 100.0 - (defect_ratio * 100.0 * 5.0))

        weighted_score = raw_score * weight
        weighted_total += weighted_score

        dimension_scores[dim] = DQDimensionScore(
            dimension_code=dim,
            dimension_name=name,
            weight=weight,
            records_evaluated=rec_count,
            issues_detected=iss_count,
            raw_score=raw_score,
            weighted_score=weighted_score,
        )

    return DQScoreSummary(
        overall_dq_score=min(100.0, max(0.0, weighted_total)),
        total_records_evaluated=total_records,
        total_issues_detected=total_issues,
        dimension_scores=dimension_scores,
        severity_breakdown=severity_counts,
    )

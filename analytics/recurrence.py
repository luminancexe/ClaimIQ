"""Recurrence pattern clustering and repeat offender analytics."""

from typing import Optional, List, Dict, Any
import pymysql
from analytics.config import AnalyticsConfig
from analytics.models import RecurrencePattern, RecurrenceSummary
from analytics.database import execute_analytical_query
from qa.registry import get_rule


def calculate_recurrence_patterns(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> RecurrenceSummary:
    """Identify recurring defect clusters and repeat offender patterns across entities."""
    if conn is None:
        # Standalone simulated dry-run default
        patterns = [
            RecurrencePattern(
                entity_type="PROVIDER",
                entity_identifier="PRV-2026-0000002",
                anomaly_code="E023",
                occurrence_count=4,
                first_detected_at="2026-01-10 10:00:00",
                last_detected_at="2026-02-15 14:30:00",
                recurrence_rank=1,
            ),
            RecurrencePattern(
                entity_type="PAYER",
                entity_identifier="PAY-2026-0000001",
                anomaly_code="E034",
                occurrence_count=3,
                first_detected_at="2026-01-15 09:15:00",
                last_detected_at="2026-02-20 11:45:00",
                recurrence_rank=2,
            ),
        ]
        return RecurrenceSummary(
            recurring_cluster_count=2,
            top_repeat_entities=patterns,
            repeat_issue_rate=23.33,
            total_repeating_occurrences=7,
        )

    # 1. Provider-level recurrence
    prov_sql = """
        SELECT 
            'PROVIDER' AS entity_type,
            COALESCE(p.provider_reference, CONCAT('PROV-', c.billing_provider_id)) AS entity_identifier,
            r.rule_code,
            COUNT(i.issue_id) AS occ_count,
            MIN(i.detected_at) AS first_dt,
            MAX(i.detected_at) AS last_dt
        FROM issues i
        JOIN claims c ON i.claim_id = c.claim_id
        JOIN qa_rules r ON i.rule_id = r.rule_id
        LEFT JOIN providers p ON c.billing_provider_id = p.provider_id
        GROUP BY p.provider_reference, c.billing_provider_id, r.rule_code
        HAVING occ_count >= 2
    """
    prov_rows = execute_analytical_query(conn, prov_sql)

    # 2. Payer-level recurrence
    payer_sql = """
        SELECT 
            'PAYER' AS entity_type,
            COALESCE(py.payer_reference, CONCAT('PAYER-', c.payer_id)) AS entity_identifier,
            r.rule_code,
            COUNT(i.issue_id) AS occ_count,
            MIN(i.detected_at) AS first_dt,
            MAX(i.detected_at) AS last_dt
        FROM issues i
        JOIN claims c ON i.claim_id = c.claim_id
        JOIN qa_rules r ON i.rule_id = r.rule_id
        LEFT JOIN payers py ON c.payer_id = py.payer_id
        GROUP BY py.payer_reference, c.payer_id, r.rule_code
        HAVING occ_count >= 2
    """
    payer_rows = execute_analytical_query(conn, payer_sql)

    all_cluster_rows = prov_rows + payer_rows
    # Sort deterministically: count DESC, entity_type ASC, entity_identifier ASC, rule_code ASC
    all_cluster_rows.sort(key=lambda x: (-x["occ_count"], x["entity_type"], str(x["entity_identifier"]), x["rule_code"]))

    total_issue_rows = execute_analytical_query(conn, "SELECT COUNT(*) AS total_cnt FROM issues")
    total_issues = total_issue_rows[0]["total_cnt"] if total_issue_rows else 0

    patterns: List[RecurrencePattern] = []
    total_repeat_occurrences = 0

    for rank, r in enumerate(all_cluster_rows, start=1):
        occ = r["occ_count"]
        total_repeat_occurrences += occ

        anom_code = "UNKNOWN"
        try:
            rule_def = get_rule(r["rule_code"])
            if rule_def.anomaly_codes:
                anom_code = rule_def.anomaly_codes[0]
        except Exception:
            pass

        first_str = str(r["first_dt"]) if r["first_dt"] is not None else None
        last_str = str(r["last_dt"]) if r["last_dt"] is not None else None

        patterns.append(
            RecurrencePattern(
                entity_type=r["entity_type"],
                entity_identifier=str(r["entity_identifier"]),
                anomaly_code=anom_code,
                occurrence_count=occ,
                first_detected_at=first_str,
                last_detected_at=last_str,
                recurrence_rank=rank,
            )
        )

    repeat_rate = (float(total_repeat_occurrences) / float(total_issues) * 100.0) if total_issues > 0 else 0.0

    return RecurrenceSummary(
        recurring_cluster_count=len(patterns),
        top_repeat_entities=patterns[:15],
        repeat_issue_rate=repeat_rate,
        total_repeating_occurrences=total_repeat_occurrences,
    )

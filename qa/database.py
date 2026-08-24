"""Database Persistence and QA Metadata Synchronization for ClaimIQ Phase 5."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord, QARunTelemetry
from qa.registry import ALL_RULE_DEFINITIONS


def sync_qa_rules_to_database(conn: pymysql.Connection) -> Dict[str, int]:
    """Ensure all registered QA rule definitions exist in MySQL qa_rules table."""
    with conn.cursor() as cur:
        # Ensure categories exist
        cur.execute("SELECT category_id, category_code FROM qa_rule_categories")
        cat_map = {row["category_code"]: row["category_id"] for row in cur.fetchall()}

        sql = """
            INSERT INTO qa_rules (
                rule_code, category_id, dimension_code, default_severity_code,
                rule_name, description, sql_logic, is_active
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                category_id = VALUES(category_id),
                dimension_code = VALUES(dimension_code),
                default_severity_code = VALUES(default_severity_code),
                rule_name = VALUES(rule_name),
                description = VALUES(description),
                sql_logic = VALUES(sql_logic),
                is_active = VALUES(is_active)
        """
        
        tuples = [
            (
                r.rule_code,
                cat_map.get(r.category_code, r.category_id),
                r.dimension_code,
                r.default_severity_code,
                r.rule_name,
                r.description,
                r.sql_logic,
                1 if r.is_active else 0,
            )
            for r in ALL_RULE_DEFINITIONS
        ]

        cur.executemany(sql, tuples)
        conn.commit()

        # Fetch and return rule_code -> rule_id map
        cur.execute("SELECT rule_id, rule_code FROM qa_rules")
        return {row["rule_code"]: row["rule_id"] for row in cur.fetchall()}


def get_db_rule_id_map(conn: pymysql.Connection) -> Dict[str, int]:
    """Retrieve mapping of rule_code to MySQL rule_id."""
    with conn.cursor() as cur:
        cur.execute("SELECT rule_id, rule_code FROM qa_rules")
        rows = cur.fetchall()
        if not rows:
            return sync_qa_rules_to_database(conn)
        return {row["rule_code"]: row["rule_id"] for row in rows}


def record_qa_execution_run(
    conn: pymysql.Connection,
    run_reference: str,
    batch_identifier: str,
    started_at: datetime,
    completed_at: Optional[datetime],
    status: str,
    total_rules_evaluated: int,
    total_records_evaluated: int,
    total_issues_detected: int,
    dq_score: Optional[float],
) -> int:
    """Insert a new QA execution run record into qa_execution_runs."""
    sql = """
        INSERT INTO qa_execution_runs (
            run_reference, batch_identifier, started_at, completed_at, status,
            total_rules_evaluated, total_records_evaluated, total_issues_detected, dq_score
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    with conn.cursor() as cur:
        cur.execute(sql, (
            run_reference,
            batch_identifier,
            started_at,
            completed_at,
            status,
            total_rules_evaluated,
            total_records_evaluated,
            total_issues_detected,
            round(dq_score, 2) if dq_score is not None else None,
        ))
        conn.commit()
        return cur.lastrowid


def save_qa_results(
    conn: pymysql.Connection,
    run_id: int,
    telemetry_list: List[QARunTelemetry],
    rule_id_map: Dict[str, int],
) -> int:
    """Batch insert per-rule execution telemetry records into qa_results."""
    if not telemetry_list:
        return 0

    sql = """
        INSERT INTO qa_results (
            run_id, rule_id, records_evaluated, issues_detected, execution_duration_ms, run_status
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        )
    """

    tuples = [
        (
            run_id,
            rule_id_map.get(t.rule_code, 1),
            t.records_evaluated,
            t.issues_detected,
            t.execution_duration_ms,
            t.run_status,
        )
        for t in telemetry_list
    ]

    with conn.cursor() as cur:
        cur.executemany(sql, tuples)
        conn.commit()

    return len(telemetry_list)


def save_detected_issues(
    conn: pymysql.Connection,
    detections: List[QADetectionRecord],
    rule_id_map: Dict[str, int],
) -> int:
    """Persist detected QA defect records into MySQL issues table."""
    if not detections:
        return 0

    sql = """
        INSERT INTO issues (
            issue_reference, rule_id, claim_id, dimension_code, severity_code,
            current_status_code, detected_at, variance_amount
        ) VALUES (
            %s, %s, %s, %s, %s, 'Detected', NOW(6), %s
        ) ON DUPLICATE KEY UPDATE
            current_status_code = VALUES(current_status_code),
            variance_amount = VALUES(variance_amount)
    """

    now_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    tuples = [
        (
            f"ISS-{now_str}-{idx+1:05d}",
            rule_id_map.get(d.rule_code, 1),
            d.claim_id,
            d.dimension_code,
            d.severity_code,
            d.variance_amount,
        )
        for idx, d in enumerate(detections)
    ]

    with conn.cursor() as cur:
        cur.executemany(sql, tuples)
        conn.commit()

    return len(detections)

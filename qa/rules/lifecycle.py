"""Claim Lifecycle & State Machine QA Rules (E043–E050)."""

from typing import List, Tuple, Any
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord

LIFECYCLE_RULES = [
    QARuleDefinition(
        rule_code="R-E043",
        rule_name="Illegal Direct Status Transition (Denied to Paid)",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="claim_status_history",
        target_column="previous_status_code",
        description="Detects impossible state transitions in audit history bypassing mandatory adjudication workflows.",
        sql_logic="""
            SELECT h.history_id, h.claim_id, h.previous_status_code, h.new_status_code, c.claim_reference
            FROM claim_status_history h
            JOIN claims c ON h.claim_id = c.claim_id
            WHERE h.previous_status_code = 'Denied'
              AND h.new_status_code = 'Paid'
        """,
        anomaly_codes=["E043"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E044",
        rule_name="Paid Claim Zero Paid Ledger Inconsistency",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="reconciliations",
        target_column="total_paid",
        description="Detects claims marked in Paid status whose reconciliation total_paid amount is zero.",
        sql_logic="""
            SELECT r.reconciliation_id, r.claim_id, r.total_paid, c.claim_reference, c.current_status_code
            FROM reconciliations r
            JOIN claims c ON r.claim_id = c.claim_id
            WHERE c.current_status_code = 'Paid'
              AND r.total_paid = 0.00
              AND c.total_billed_amount > 0.00
        """,
        anomaly_codes=["E044"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E045",
        rule_name="Denied Claim with Active Payment Disbursements",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="claims",
        target_column="current_status_code",
        description="Detects claims in Denied status that contain active positive cash payments.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.current_status_code, SUM(p.paid_amount) AS total_paid
            FROM claims c
            JOIN payments p ON c.claim_id = p.claim_id
            WHERE c.current_status_code = 'Denied'
              AND p.paid_amount > 0.00
            GROUP BY c.claim_id, c.claim_reference, c.current_status_code
        """,
        anomaly_codes=["E045"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E046",
        rule_name="Rejected Claim with Payment Disbursements",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="claims",
        target_column="current_status_code",
        description="Detects claims in Rejected pre-adjudication status that contain cash disbursements.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.current_status_code, SUM(p.paid_amount) AS total_paid
            FROM claims c
            JOIN payments p ON c.claim_id = p.claim_id
            WHERE c.current_status_code = 'Rejected'
              AND p.paid_amount > 0.00
            GROUP BY c.claim_id, c.claim_reference, c.current_status_code
        """,
        anomaly_codes=["E046"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E047",
        rule_name="Pending Review Claim with Finalized Payment",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Medium",
        target_table="claims",
        target_column="current_status_code",
        description="Detects in-flight claims in Pending review status that have received payment allocations.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.current_status_code, SUM(p.paid_amount) AS total_paid
            FROM claims c
            JOIN payments p ON c.claim_id = p.claim_id
            WHERE c.current_status_code = 'Pending'
              AND p.paid_amount > 0.00
            GROUP BY c.claim_id, c.claim_reference, c.current_status_code
        """,
        anomaly_codes=["E047"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E048",
        rule_name="Unadjudicated Claim Flagged as Reconciled",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Medium",
        target_table="claims",
        target_column="is_reconciled",
        description="Detects in-flight unadjudicated claims (Submitted) prematurely flagged as is_reconciled = 1.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.current_status_code, c.is_reconciled
            FROM claims c
            WHERE c.current_status_code = 'Submitted'
              AND c.is_reconciled = 1
        """,
        anomaly_codes=["E048"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E049",
        rule_name="Finalized Paid Claim Missing Adjudication Timestamp",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Medium",
        target_table="claims",
        target_column="adjudication_date",
        description="Detects finalized Paid claims that lack recorded adjudication dates.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.current_status_code, c.adjudication_date
            FROM claims c
            WHERE c.current_status_code = 'Paid'
              AND c.adjudication_date IS NULL
        """,
        anomaly_codes=["E049"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E050",
        rule_name="Redundant Consecutive Terminal State Transition",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Low",
        target_table="claim_status_history",
        target_column="new_status_code",
        description="Detects duplicate consecutive transitions into the same terminal status (Paid -> Paid).",
        sql_logic="""
            SELECT h.history_id, h.claim_id, h.previous_status_code, h.new_status_code, c.claim_reference
            FROM claim_status_history h
            JOIN claims c ON h.claim_id = c.claim_id
            WHERE h.previous_status_code = 'Paid'
              AND h.new_status_code = 'Paid'
        """,
        anomaly_codes=["E050"],
        detection_method="SQL_SET",
    ),
]


def evaluate_lifecycle_rule(conn: pymysql.Connection, rule: QARuleDefinition) -> Tuple[int, List[QADetectionRecord]]:
    """Execute a lifecycle SQL rule and collect detection findings."""
    detections: List[QADetectionRecord] = []

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total_count FROM {rule.target_table}")
        records_evaluated = cur.fetchone()["total_count"]

        cur.execute(rule.sql_logic)
        rows = cur.fetchall()

        for r in rows:
            pk_col = f"{rule.target_table[:-1] if rule.target_table.endswith('s') else rule.target_table}_id"
            if rule.target_table == "claim_status_history":
                pk_col = "history_id"
            elif rule.target_table == "reconciliations":
                pk_col = "reconciliation_id"

            record_id = r.get(pk_col, 0)
            biz_ref = r.get("claim_reference") or f"{rule.target_table.upper()}-{record_id}"

            claim_id = r.get("claim_id") if "claim_id" in r else (record_id if rule.target_table == "claims" else None)

            det = QADetectionRecord(
                rule_code=rule.rule_code,
                anomaly_code=rule.anomaly_codes[0],
                target_table=rule.target_table,
                target_record_id=record_id,
                target_business_reference=biz_ref,
                target_column=rule.target_column,
                detected_value=str(r.get(rule.target_column)),
                severity_code=rule.default_severity_code,
                dimension_code=rule.dimension_code,
                explanation=f"{rule.rule_name}: lifecycle conflict on {rule.target_table} ID {record_id}",
                claim_id=claim_id,
            )
            detections.append(det)

    return records_evaluated, detections

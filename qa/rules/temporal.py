"""Temporal & Chronological QA Rules (E034–E042)."""

from typing import List, Tuple, Any
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord

TEMPORAL_RULES = [
    QARuleDefinition(
        rule_code="R-E034",
        rule_name="Clinical DOS Precedes Claim Submission",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="High",
        target_table="encounters",
        target_column="date_of_service",
        description="Detects clinical encounters where date of service occurs after the claim submission date.",
        sql_logic="""
            SELECT e.encounter_id, e.encounter_reference, e.date_of_service, c.claim_id, c.claim_reference, c.submission_date
            FROM encounters e
            JOIN claims c ON e.encounter_id = c.encounter_id
            WHERE e.date_of_service > c.submission_date
        """,
        anomaly_codes=["E034"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E035",
        rule_name="Claim Submission Precedes Adjudication",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="High",
        target_table="claims",
        target_column="submission_date",
        description="Detects claims where electronic submission date is recorded after payer adjudication date.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.submission_date, c.adjudication_date
            FROM claims c
            WHERE c.adjudication_date IS NOT NULL
              AND c.submission_date > c.adjudication_date
        """,
        anomaly_codes=["E035"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E036",
        rule_name="Payment Date Succeeds Claim Submission",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="High",
        target_table="payments",
        target_column="payment_date",
        description="Detects cash payments processed on dates prior to original claim transmission.",
        sql_logic="""
            SELECT p.payment_id, p.payment_reference, p.claim_id, p.payment_date, c.submission_date
            FROM payments p
            JOIN claims c ON p.claim_id = c.claim_id
            WHERE p.payment_date < c.submission_date
        """,
        anomaly_codes=["E036"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E037",
        rule_name="Payment Date Succeeds Adjudication Decision",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="High",
        target_table="payments",
        target_column="payment_date",
        description="Detects payments dated before payer formal adjudication date.",
        sql_logic="""
            SELECT p.payment_id, p.payment_reference, p.claim_id, p.payment_date, c.adjudication_date
            FROM payments p
            JOIN claims c ON p.claim_id = c.claim_id
            WHERE c.adjudication_date IS NOT NULL
              AND p.payment_date < c.adjudication_date
        """,
        anomaly_codes=["E037"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E038",
        rule_name="Remittance Generation Succeeds Adjudication",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="Medium",
        target_table="remittances",
        target_column="remittance_date",
        description="Detects remittance advice batches created prior to claim adjudication decisions.",
        sql_logic="""
            SELECT r.remittance_id, r.remittance_reference, r.remittance_date, c.adjudication_date
            FROM remittances r
            JOIN payments p ON r.remittance_id = p.remittance_id
            JOIN claims c ON p.claim_id = c.claim_id
            WHERE c.adjudication_date IS NOT NULL
              AND r.remittance_date < c.adjudication_date
            GROUP BY r.remittance_id, r.remittance_reference, r.remittance_date, c.adjudication_date
        """,
        anomaly_codes=["E038"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E039",
        rule_name="Denial Notice Succeeds Claim Submission",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="High",
        target_table="denials",
        target_column="denial_date",
        description="Detects payer denial notifications dated before original claim transmission.",
        sql_logic="""
            SELECT d.denial_id, d.claim_id, d.denial_date, c.submission_date, c.claim_reference
            FROM denials d
            JOIN claims c ON d.claim_id = c.claim_id
            WHERE d.denial_date < c.submission_date
        """,
        anomaly_codes=["E039"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E040",
        rule_name="Inpatient Discharge Succeeds Admission Date",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="High",
        target_table="encounters",
        target_column="discharge_date",
        description="Detects encounters where hospital discharge date occurs before admission date of service.",
        sql_logic="""
            SELECT e.encounter_id, e.encounter_reference, e.date_of_service, e.discharge_date
            FROM encounters e
            WHERE e.discharge_date IS NOT NULL
              AND e.discharge_date < e.date_of_service
        """,
        anomaly_codes=["E040"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E041",
        rule_name="Future-Dated Claim Submission Event",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="High",
        target_table="claims",
        target_column="submission_date",
        description="Detects claim submission events carrying future timestamps exceeding current operating calendar.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.submission_date
            FROM claims c
            WHERE c.submission_date > '2026-12-31'
        """,
        anomaly_codes=["E041"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E042",
        rule_name="Claim Submission Succeeds Patient Date of Birth",
        category_code="TEMPORAL",
        category_id=5,
        dimension_code="Temporal",
        default_severity_code="Critical",
        target_table="claims",
        target_column="submission_date",
        description="Detects claims submitted on dates prior to the patient's biological date of birth.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.submission_date, p.patient_id, p.date_of_birth
            FROM claims c
            JOIN patients p ON c.patient_id = p.patient_id
            WHERE c.submission_date < p.date_of_birth
        """,
        anomaly_codes=["E042"],
        detection_method="SQL_SET",
    ),
]


def evaluate_temporal_rule(conn: pymysql.Connection, rule: QARuleDefinition) -> Tuple[int, List[QADetectionRecord]]:
    """Execute a temporal SQL rule and collect detection findings."""
    detections: List[QADetectionRecord] = []

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total_count FROM {rule.target_table}")
        records_evaluated = cur.fetchone()["total_count"]

        cur.execute(rule.sql_logic)
        rows = cur.fetchall()

        for r in rows:
            pk_col = f"{rule.target_table[:-1] if rule.target_table.endswith('s') else rule.target_table}_id"
            record_id = r.get(pk_col, 0)
            biz_ref = r.get("claim_reference") or r.get("payment_reference") or r.get("remittance_reference") or r.get("encounter_reference")

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
                explanation=f"{rule.rule_name}: chronological violation on {rule.target_table} ID {record_id}",
                claim_id=claim_id,
            )
            detections.append(det)

    return records_evaluated, detections

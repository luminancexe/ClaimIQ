"""Duplication & Uniqueness QA Rules (E011–E015)."""

from typing import List, Tuple, Any
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord

DUPLICATION_RULES = [
    QARuleDefinition(
        rule_code="R-E011",
        rule_name="Duplicate Claim Header Detection",
        category_code="UNIQUENESS",
        category_id=3,
        dimension_code="Uniqueness",
        default_severity_code="High",
        target_table="claims",
        target_column="claim_reference",
        description="Detects duplicate claim submissions sharing identical encounter, patient, provider, and total billed amount.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.encounter_id, c.patient_id, c.billing_provider_id, c.total_billed_amount
            FROM claims c
            WHERE c.claim_reference LIKE 'DUP-%'
               OR c.claim_id IN (
                   SELECT c2.claim_id
                   FROM claims c2
                   JOIN claims c3 ON c2.encounter_id = c3.encounter_id
                                 AND c2.patient_id = c3.patient_id
                                 AND c2.billing_provider_id = c3.billing_provider_id
                                 AND c2.claim_id > c3.claim_id
               )
        """,
        anomaly_codes=["E011"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E012",
        rule_name="Duplicate Claim Line Item Detection",
        category_code="UNIQUENESS",
        category_id=3,
        dimension_code="Uniqueness",
        default_severity_code="High",
        target_table="claim_lines",
        target_column="cpt_code",
        description="Detects repeated service lines with identical CPT code, units, and price billed within the same claim.",
        sql_logic="""
            SELECT cl.claim_line_id, cl.claim_id, cl.line_number, cl.cpt_code, cl.line_billed_amount
            FROM claim_lines cl
            WHERE cl.claim_line_id IN (
                SELECT cl1.claim_line_id
                FROM claim_lines cl1
                JOIN claim_lines cl2 ON cl1.claim_id = cl2.claim_id
                                    AND cl1.cpt_code = cl2.cpt_code
                                    AND cl1.units = cl2.units
                                    AND cl1.unit_price = cl2.unit_price
                                    AND cl1.claim_line_id > cl2.claim_line_id
            )
        """,
        anomaly_codes=["E012"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E013",
        rule_name="Duplicate Payment Transaction Detection",
        category_code="UNIQUENESS",
        category_id=3,
        dimension_code="Uniqueness",
        default_severity_code="High",
        target_table="payments",
        target_column="paid_amount",
        description="Detects duplicate cash disbursements credited against the same claim from the same remittance.",
        sql_logic="""
            SELECT p.payment_id, p.payment_reference, p.claim_id, p.remittance_id, p.paid_amount
            FROM payments p
            WHERE p.payment_reference LIKE 'DUP-%'
               OR p.payment_id IN (
                   SELECT p1.payment_id
                   FROM payments p1
                   JOIN payments p2 ON p1.claim_id = p2.claim_id
                                   AND p1.remittance_id = p2.remittance_id
                                   AND p1.paid_amount = p2.paid_amount
                                   AND p1.payment_id > p2.payment_id
               )
        """,
        anomaly_codes=["E013"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E014",
        rule_name="Duplicate Remittance Trace Number Detection",
        category_code="UNIQUENESS",
        category_id=3,
        dimension_code="Uniqueness",
        default_severity_code="Medium",
        target_table="remittances",
        target_column="check_trace_number",
        description="Detects duplicate check/EFT trace numbers or logical duplicate check traces across remittance batches.",
        sql_logic="""
            SELECT r.remittance_id, r.remittance_reference, r.check_trace_number
            FROM remittances r
            WHERE r.check_trace_number LIKE '%-DUP%'
               OR r.remittance_id IN (
                   SELECT r1.remittance_id
                   FROM remittances r1
                   JOIN remittances r2 ON r1.check_trace_number = r2.check_trace_number
                                      AND r1.remittance_id > r2.remittance_id
               )
        """,
        anomaly_codes=["E014"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E015",
        rule_name="Duplicate Clinical Encounter Detection",
        category_code="UNIQUENESS",
        category_id=3,
        dimension_code="Uniqueness",
        default_severity_code="High",
        target_table="encounters",
        target_column="encounter_reference",
        description="Detects duplicate clinical encounters logged for the same patient, clinician, and date of service.",
        sql_logic="""
            SELECT e.encounter_id, e.encounter_reference, e.patient_id, e.provider_id, e.date_of_service
            FROM encounters e
            WHERE e.encounter_reference LIKE 'DUP-%'
               OR e.encounter_id IN (
                   SELECT e1.encounter_id
                   FROM encounters e1
                   JOIN encounters e2 ON e1.patient_id = e2.patient_id
                                     AND e1.provider_id = e2.provider_id
                                     AND e1.date_of_service = e2.date_of_service
                                     AND e1.encounter_type = e2.encounter_type
                                     AND e1.encounter_id > e2.encounter_id
               )
        """,
        anomaly_codes=["E015"],
        detection_method="SQL_SET",
    ),
]


def evaluate_duplication_rule(conn: pymysql.Connection, rule: QARuleDefinition) -> Tuple[int, List[QADetectionRecord]]:
    """Execute a duplication SQL rule and collect detection findings."""
    detections: List[QADetectionRecord] = []

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total_count FROM {rule.target_table}")
        records_evaluated = cur.fetchone()["total_count"]

        cur.execute(rule.sql_logic)
        rows = cur.fetchall()

        for r in rows:
            pk_col = f"{rule.target_table[:-1] if rule.target_table.endswith('s') else rule.target_table}_id"
            if rule.target_table == "claim_lines":
                pk_col = "claim_line_id"

            record_id = r.get(pk_col, 0)
            biz_ref = r.get("claim_reference") or r.get("payment_reference") or r.get("remittance_reference") or r.get("encounter_reference") or f"{rule.target_table.upper()}-{record_id}"

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
                explanation=f"{rule.rule_name}: duplicate entity detected on {rule.target_table} ID {record_id} ({biz_ref})",
                claim_id=claim_id,
            )
            detections.append(det)

    return records_evaluated, detections

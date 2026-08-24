"""Referential Integrity & Cross-Entity QA Rules (E016–E022)."""

from typing import List, Tuple, Any
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord

REFERENTIAL_RULES = [
    QARuleDefinition(
        rule_code="R-E016",
        rule_name="Provider Facility State Alignment",
        category_code="REFERENTIAL",
        category_id=6,
        dimension_code="Referential Integrity",
        default_severity_code="Medium",
        target_table="providers",
        target_column="facility_id",
        description="Verifies that providers are assigned to facilities within valid geographic operating states.",
        sql_logic="""
            SELECT p.provider_id, p.provider_reference, p.facility_id, f.state AS fac_state
            FROM providers p
            JOIN facilities f ON p.facility_id = f.facility_id
            WHERE f.state NOT IN ('CA', 'TX', 'NY', 'FL', 'IL', 'OH', 'PA')
               OR (p.facility_id IS NOT NULL AND f.facility_id IS NULL)
        """,
        anomaly_codes=["E016"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E017",
        rule_name="Claim Payer and Policy Plan Alignment",
        category_code="REFERENTIAL",
        category_id=6,
        dimension_code="Referential Integrity",
        default_severity_code="High",
        target_table="claims",
        target_column="payer_id",
        description="Detects claims submitted to a payer that does not underwrite the patient's coverage plan.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.payer_id, c.patient_id
            FROM claims c
            WHERE NOT EXISTS (
                SELECT 1
                FROM patient_coverage pc
                JOIN insurance_plans ip ON pc.plan_id = ip.plan_id
                WHERE pc.patient_id = c.patient_id
                  AND ip.payer_id = c.payer_id
            )
        """,
        anomaly_codes=["E017"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E018",
        rule_name="Inpatient Hospital Provider Specialty Alignment",
        category_code="REFERENTIAL",
        category_id=6,
        dimension_code="Referential Integrity",
        default_severity_code="Medium",
        target_table="encounters",
        target_column="provider_id",
        description="Detects inpatient hospitalization encounters assigned to outpatient-only clinician specialties.",
        sql_logic="""
            SELECT e.encounter_id, e.encounter_reference, e.provider_id, p.specialty
            FROM encounters e
            JOIN providers p ON e.provider_id = p.provider_id
            WHERE e.encounter_type = 'Inpatient Hospital'
              AND p.specialty IN ('Dermatology', 'Psychiatry', 'Physical Therapy')
        """,
        anomaly_codes=["E018"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E019",
        rule_name="Claim Submission Active Patient Policy Check",
        category_code="REFERENTIAL",
        category_id=6,
        dimension_code="Referential Integrity",
        default_severity_code="High",
        target_table="claims",
        target_column="payer_id",
        description="Detects claims submitted to a payer where the patient possesses no insurance policy on record.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.patient_id, c.payer_id
            FROM claims c
            WHERE c.payer_id NOT IN (
                SELECT DISTINCT ip.payer_id
                FROM patient_coverage pc
                JOIN insurance_plans ip ON pc.plan_id = ip.plan_id
                WHERE pc.patient_id = c.patient_id
            )
        """,
        anomaly_codes=["E019"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E020",
        rule_name="Claim Line Cross-Claim Integrity",
        category_code="REFERENTIAL",
        category_id=6,
        dimension_code="Referential Integrity",
        default_severity_code="High",
        target_table="claim_lines",
        target_column="claim_id",
        description="Detects claim line items reallocated or linked to discordant parent claims.",
        sql_logic="""
            SELECT cl.claim_line_id, cl.claim_id, c.claim_reference
            FROM claim_lines cl
            LEFT JOIN claims c ON cl.claim_id = c.claim_id
            WHERE c.claim_id IS NULL
        """,
        anomaly_codes=["E020"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E021",
        rule_name="Payment Remittance and Claim Payer Consistency",
        category_code="REFERENTIAL",
        category_id=6,
        dimension_code="Referential Integrity",
        default_severity_code="High",
        target_table="payments",
        target_column="claim_id",
        description="Detects cash disbursements allocated to claims billed to a different payer than the remittance header.",
        sql_logic="""
            SELECT p.payment_id, p.payment_reference, p.claim_id, p.remittance_id, r.payer_id AS remit_payer_id, c.payer_id AS claim_payer_id
            FROM payments p
            JOIN remittances r ON p.remittance_id = r.remittance_id
            JOIN claims c ON p.claim_id = c.claim_id
            WHERE r.payer_id != c.payer_id
        """,
        anomaly_codes=["E021"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E022",
        rule_name="Remittance Batch Payer Alignment",
        category_code="REFERENTIAL",
        category_id=6,
        dimension_code="Referential Integrity",
        default_severity_code="High",
        target_table="remittances",
        target_column="payer_id",
        description="Detects remittance batches whose paying entity does not match the claims being reimbursed.",
        sql_logic="""
            SELECT r.remittance_id, r.remittance_reference, r.payer_id
            FROM remittances r
            JOIN payments p ON r.remittance_id = p.remittance_id
            JOIN claims c ON p.claim_id = c.claim_id
            WHERE r.payer_id != c.payer_id
            GROUP BY r.remittance_id, r.remittance_reference, r.payer_id
        """,
        anomaly_codes=["E022"],
        detection_method="SQL_SET",
    ),
]


def evaluate_referential_rule(conn: pymysql.Connection, rule: QARuleDefinition) -> Tuple[int, List[QADetectionRecord]]:
    """Execute a referential integrity SQL rule and collect detection findings."""
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
            biz_ref = r.get("claim_reference") or r.get("payment_reference") or r.get("remittance_reference") or r.get("provider_reference") or r.get("encounter_reference")

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
                explanation=f"{rule.rule_name}: referential mismatch on {rule.target_table} ID {record_id}",
                claim_id=claim_id,
            )
            detections.append(det)

    return records_evaluated, detections

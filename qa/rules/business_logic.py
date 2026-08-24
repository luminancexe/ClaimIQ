"""Business Logic & Operational QA Rules (E051–E060)."""

from typing import List, Tuple, Any
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord

BUSINESS_LOGIC_RULES = [
    QARuleDefinition(
        rule_code="R-E051",
        rule_name="Positive-Billed Claim Header Lacks Service Lines",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="claims",
        target_column="claim_id",
        description="Detects positive billed claims that possess zero itemized service lines.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.total_billed_amount
            FROM claims c
            LEFT JOIN claim_lines cl ON c.claim_id = cl.claim_id
            WHERE c.total_billed_amount > 0.00
              AND cl.claim_line_id IS NULL
        """,
        anomaly_codes=["E051"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E052",
        rule_name="Claim Patient Discordant with Encounter Patient",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Critical",
        target_table="claims",
        target_column="patient_id",
        description="Detects claims billed for a patient that differs from the clinical encounter patient.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.patient_id, e.patient_id AS enc_patient_id
            FROM claims c
            JOIN encounters e ON c.encounter_id = e.encounter_id
            WHERE c.patient_id != e.patient_id
        """,
        anomaly_codes=["E052"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E053",
        rule_name="Claim Billing Provider Discordant with Encounter Clinician",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Medium",
        target_table="claims",
        target_column="billing_provider_id",
        description="Detects claims where billing provider does not match the rendering clinician on the encounter.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.billing_provider_id, e.provider_id AS enc_provider_id
            FROM claims c
            JOIN encounters e ON c.encounter_id = e.encounter_id
            WHERE c.billing_provider_id != e.provider_id
        """,
        anomaly_codes=["E053"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E054",
        rule_name="Claim Submitted Outside Statutory Timely Filing Limit",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="claims",
        target_column="submission_date",
        description="Detects claims submitted past the payer contractual timely filing window from DOS.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.submission_date, e.date_of_service, p.timely_filing_days,
                   DATEDIFF(c.submission_date, e.date_of_service) AS days_elapsed
            FROM claims c
            JOIN encounters e ON c.encounter_id = e.encounter_id
            JOIN payers p ON c.payer_id = p.payer_id
            WHERE DATEDIFF(c.submission_date, e.date_of_service) > p.timely_filing_days
        """,
        anomaly_codes=["E054"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E055",
        rule_name="Payment Allocated to In-Flight Submitted Claim",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="claims",
        target_column="current_status_code",
        description="Detects claims in Submitted status that contain recorded cash payment transactions.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.current_status_code, SUM(p.paid_amount) AS total_paid
            FROM claims c
            JOIN payments p ON c.claim_id = p.claim_id
            WHERE c.current_status_code = 'Submitted'
              AND p.paid_amount > 0.00
            GROUP BY c.claim_id, c.claim_reference, c.current_status_code
        """,
        anomaly_codes=["E055"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E056",
        rule_name="Contradictory Denial Record Attached to Paid Claim",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="denials",
        target_column="claim_id",
        description="Detects active denial notices linked to claims fully adjudicated in Paid status.",
        sql_logic="""
            SELECT d.denial_id, d.claim_id, d.denial_code, c.claim_reference, c.current_status_code
            FROM denials d
            JOIN claims c ON d.claim_id = c.claim_id
            WHERE c.current_status_code = 'Paid'
        """,
        anomaly_codes=["E056"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E057",
        rule_name="Reconciliation Flagged Balanced Despite Non-Zero Variance",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Critical",
        target_table="reconciliations",
        target_column="reconciliation_status",
        description="Detects reconciliations marked BALANCED when variance_amount is non-zero.",
        sql_logic="""
            SELECT r.reconciliation_id, r.claim_id, r.variance_amount, r.reconciliation_status
            FROM reconciliations r
            WHERE r.reconciliation_status = 'BALANCED'
              AND r.variance_amount != 0.00
        """,
        anomaly_codes=["E057"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E058",
        rule_name="Reconciliation Flagged Unbalanced with Zero Variance",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Medium",
        target_table="reconciliations",
        target_column="reconciliation_status",
        description="Detects reconciliations marked UNBALANCED when variance_amount is exactly 0.00.",
        sql_logic="""
            SELECT r.reconciliation_id, r.claim_id, r.variance_amount, r.reconciliation_status
            FROM reconciliations r
            WHERE r.reconciliation_status = 'UNBALANCED'
              AND r.variance_amount = 0.00
        """,
        anomaly_codes=["E058"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E059",
        rule_name="Clinical DOS Outside Patient Active Coverage Window",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="High",
        target_table="patient_coverage",
        target_column="effective_date",
        description="Detects encounters occurring before the patient's coverage policy effective start date.",
        sql_logic="""
            SELECT pc.coverage_id, pc.patient_id, pc.effective_date, e.date_of_service, e.encounter_id
            FROM patient_coverage pc
            JOIN encounters e ON pc.patient_id = e.patient_id
            WHERE e.date_of_service < pc.effective_date
        """,
        anomaly_codes=["E059"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E060",
        rule_name="Inpatient Hospitalization Outpatient CPT Coding Conflict",
        category_code="BUSINESS_LOGIC",
        category_id=7,
        dimension_code="Accuracy",
        default_severity_code="Low",
        target_table="claim_lines",
        target_column="cpt_code",
        description="Detects minor outpatient evaluation & management codes billed during acute inpatient hospital stays.",
        sql_logic="""
            SELECT cl.claim_line_id, cl.claim_id, cl.cpt_code, e.encounter_type
            FROM claim_lines cl
            JOIN claims c ON cl.claim_id = c.claim_id
            JOIN encounters e ON c.encounter_id = e.encounter_id
            WHERE e.encounter_type = 'Inpatient Hospital'
              AND cl.cpt_code IN ('99211')
        """,
        anomaly_codes=["E060"],
        detection_method="SQL_SET",
    ),
]


def evaluate_business_logic_rule(conn: pymysql.Connection, rule: QARuleDefinition) -> Tuple[int, List[QADetectionRecord]]:
    """Execute a business logic SQL rule and collect detection findings."""
    detections: List[QADetectionRecord] = []

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total_count FROM {rule.target_table}")
        records_evaluated = cur.fetchone()["total_count"]

        cur.execute(rule.sql_logic)
        rows = cur.fetchall()

        for r in rows:
            pk_col = f"{rule.target_table[:-1] if rule.target_table.endswith('s') else rule.target_table}_id"
            if rule.target_table == "patient_coverage":
                pk_col = "coverage_id"
            elif rule.target_table == "reconciliations":
                pk_col = "reconciliation_id"
            elif rule.target_table == "claim_lines":
                pk_col = "claim_line_id"

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
                explanation=f"{rule.rule_name}: operational logic discrepancy on {rule.target_table} ID {record_id}",
                claim_id=claim_id,
            )
            detections.append(det)

    return records_evaluated, detections

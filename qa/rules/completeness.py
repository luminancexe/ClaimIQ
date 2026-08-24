"""Completeness QA Rules (E001–E010)."""

from typing import List, Tuple, Any
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord

COMPLETENESS_RULES = [
    QARuleDefinition(
        rule_code="R-E001",
        rule_name="Mandatory Patient State Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Low",
        target_table="patients",
        target_column="address_state",
        description="Verifies that patient geographic state is populated and non-empty.",
        sql_logic="SELECT patient_id, patient_reference, address_state FROM patients WHERE address_state IS NULL OR address_state = ''",
        anomaly_codes=["E001"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E002",
        rule_name="Provider Facility Assignment Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Medium",
        target_table="providers",
        target_column="facility_id",
        description="Verifies that clinician records maintain mandatory facility linkages.",
        sql_logic="SELECT provider_id, provider_reference, facility_id FROM providers WHERE facility_id IS NULL",
        anomaly_codes=["E002"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E003",
        rule_name="Coverage Policy Group Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Low",
        target_table="patient_coverage",
        target_column="group_number",
        description="Verifies that patient commercial coverage policies contain group numbers.",
        sql_logic="SELECT coverage_id, member_id, group_number FROM patient_coverage WHERE group_number IS NULL OR group_number = ''",
        anomaly_codes=["E003"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E004",
        rule_name="Claim Line Procedure Description Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Low",
        target_table="claim_lines",
        target_column="procedure_description",
        description="Verifies that itemized claim service lines include narrative procedure descriptions.",
        sql_logic="SELECT claim_line_id, claim_id, procedure_description FROM claim_lines WHERE procedure_description IS NULL OR procedure_description = ''",
        anomaly_codes=["E004"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E005",
        rule_name="Inpatient Discharge Timestamp Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Medium",
        target_table="encounters",
        target_column="discharge_date",
        description="Verifies that inpatient hospital encounters include recorded discharge dates.",
        sql_logic="SELECT encounter_id, encounter_reference, discharge_date FROM encounters WHERE encounter_type = 'Inpatient Hospital' AND discharge_date IS NULL",
        anomaly_codes=["E005"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E006",
        rule_name="Adjudicated Claim Adjudication Date Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="High",
        target_table="claims",
        target_column="adjudication_date",
        description="Verifies that claims in finalized statuses (Paid, Partially Paid) have adjudication dates.",
        sql_logic="SELECT claim_id, claim_reference, adjudication_date FROM claims WHERE current_status_code IN ('Paid', 'Partially Paid') AND adjudication_date IS NULL",
        anomaly_codes=["E006"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E007",
        rule_name="Adjustment Narrative Description Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Low",
        target_table="adjustments",
        target_column="adjustment_description",
        description="Verifies that financial write-offs and contractual adjustments contain explanatory descriptions.",
        sql_logic="SELECT adjustment_id, claim_id, adjustment_description FROM adjustments WHERE adjustment_description IS NULL OR adjustment_description = ''",
        anomaly_codes=["E007"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E008",
        rule_name="Claim Status Transition Reason Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Low",
        target_table="claim_status_history",
        target_column="transition_reason",
        description="Verifies that claim lifecycle audit logs include reason notes.",
        sql_logic="SELECT history_id, claim_id, transition_reason FROM claim_status_history WHERE transition_reason IS NULL OR transition_reason = ''",
        anomaly_codes=["E008"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E009",
        rule_name="Terminated Policy End Date Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Low",
        target_table="patient_coverage",
        target_column="termination_date",
        description="Verifies that inactive/terminated patient coverage policies record termination dates.",
        sql_logic="SELECT coverage_id, member_id, termination_date FROM patient_coverage WHERE is_active = 0 AND termination_date IS NULL",
        anomaly_codes=["E009"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E010",
        rule_name="Encounter Diagnosis Description Completeness",
        category_code="COMPLETENESS",
        category_id=1,
        dimension_code="Completeness",
        default_severity_code="Medium",
        target_table="encounter_diagnoses",
        target_column="diagnosis_description",
        description="Verifies that clinical diagnosis entries retain descriptive diagnosis names.",
        sql_logic="SELECT diagnosis_id, encounter_id, diagnosis_description FROM encounter_diagnoses WHERE diagnosis_description IS NULL OR diagnosis_description = ''",
        anomaly_codes=["E010"],
        detection_method="SQL_SET",
    ),
]


def evaluate_completeness_rule(conn: pymysql.Connection, rule: QARuleDefinition) -> Tuple[int, List[QADetectionRecord]]:
    """Execute a completeness SQL rule and collect detection findings."""
    detections: List[QADetectionRecord] = []
    
    with conn.cursor() as cur:
        # Measure total records evaluated
        cur.execute(f"SELECT COUNT(*) AS total_count FROM {rule.target_table}")
        records_evaluated = cur.fetchone()["total_count"]

        cur.execute(rule.sql_logic)
        rows = cur.fetchall()

        for r in rows:
            pk_col = f"{rule.target_table[:-1] if rule.target_table.endswith('s') else rule.target_table}_id"
            if rule.target_table == "patient_coverage":
                pk_col = "coverage_id"
            elif rule.target_table == "claim_status_history":
                pk_col = "history_id"
            elif rule.target_table == "claim_lines":
                pk_col = "claim_line_id"
            elif rule.target_table == "encounter_diagnoses":
                pk_col = "diagnosis_id"

            record_id = r.get(pk_col, 0)
            biz_ref = r.get("patient_reference") or r.get("provider_reference") or r.get("claim_reference") or r.get("encounter_reference") or r.get("member_id")

            claim_id = r.get("claim_id") if "claim_id" in r else (record_id if rule.target_table == "claims" else None)

            det = QADetectionRecord(
                rule_code=rule.rule_code,
                anomaly_code=rule.anomaly_codes[0],
                target_table=rule.target_table,
                target_record_id=record_id,
                target_business_reference=biz_ref,
                target_column=rule.target_column,
                detected_value="NULL" if r.get(rule.target_column) is None else str(r.get(rule.target_column)),
                severity_code=rule.default_severity_code,
                dimension_code=rule.dimension_code,
                explanation=f"{rule.rule_name}: {rule.target_column} missing or empty on {rule.target_table} ID {record_id}",
                claim_id=claim_id,
            )
            detections.append(det)

    return records_evaluated, detections

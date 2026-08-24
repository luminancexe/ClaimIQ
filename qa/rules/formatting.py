"""Format, Syntax & Code Validity QA Rules (E061–E067)."""

import re
from typing import List, Tuple, Any
import pymysql
from generator.identifiers import validate_npi
from qa.models import QARuleDefinition, QADetectionRecord

FORMATTING_RULES = [
    QARuleDefinition(
        rule_code="R-E061",
        rule_name="Provider NPI Checksum Algorithm Validation",
        category_code="VALIDITY",
        category_id=2,
        dimension_code="Validity",
        default_severity_code="High",
        target_table="providers",
        target_column="npi",
        description="Validates 10-digit National Provider Identifier (NPI) using the CMS Luhn checksum algorithm.",
        sql_logic="SELECT provider_id, provider_reference, npi FROM providers",
        anomaly_codes=["E061"],
        detection_method="PYTHON_VALIDATION",
    ),
    QARuleDefinition(
        rule_code="R-E062",
        rule_name="CPT / HCPCS Procedure Code Syntax Conformance",
        category_code="VALIDITY",
        category_id=2,
        dimension_code="Validity",
        default_severity_code="Medium",
        target_table="claim_lines",
        target_column="cpt_code",
        description="Validates that itemized claim procedure codes adhere to 5-character CPT/HCPCS syntax standards.",
        sql_logic="""
            SELECT cl.claim_line_id, cl.claim_id, cl.cpt_code, c.claim_reference
            FROM claim_lines cl
            JOIN claims c ON cl.claim_id = c.claim_id
            WHERE cl.cpt_code = 'CPT99X'
               OR cl.cpt_code NOT REGEXP '^[0-9]{5}$|^[0-9]{4}[A-Z]$'
        """,
        anomaly_codes=["E062"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E063",
        rule_name="ICD-10-CM Clinical Diagnosis Syntax Conformance",
        category_code="VALIDITY",
        category_id=2,
        dimension_code="Validity",
        default_severity_code="Medium",
        target_table="encounter_diagnoses",
        target_column="icd10_code",
        description="Validates that encounter diagnostic codes conform to standard ICD-10-CM syntax specifications.",
        sql_logic="""
            SELECT d.diagnosis_id, d.encounter_id, d.icd10_code
            FROM encounter_diagnoses d
            WHERE d.icd10_code = 'ICD9999'
               OR d.icd10_code NOT REGEXP '^[A-Z][0-9]{2}(\\.[0-9]{1,4})?$'
        """,
        anomaly_codes=["E063"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E064",
        rule_name="NUCC Provider Specialty Taxonomy Code Conformance",
        category_code="VALIDITY",
        category_id=2,
        dimension_code="Validity",
        default_severity_code="Low",
        target_table="providers",
        target_column="taxonomy_code",
        description="Validates that provider specialty taxonomy codes conform to the 10-character NUCC standard.",
        sql_logic="""
            SELECT p.provider_id, p.provider_reference, p.taxonomy_code
            FROM providers p
            WHERE p.taxonomy_code = 'TAX-999'
               OR p.taxonomy_code NOT REGEXP '^[0-9]{9}[A-Z]$|^[0-9]{10}$'
        """,
        anomaly_codes=["E064"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E065",
        rule_name="Claim Business Reference Format Conformance",
        category_code="VALIDITY",
        category_id=2,
        dimension_code="Validity",
        default_severity_code="Low",
        target_table="claims",
        target_column="claim_reference",
        description="Validates that claim business references conform to the standard 'CLM-YYYY-NNNNNNN' schema.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference
            FROM claims c
            WHERE c.claim_reference LIKE 'BAD-REF-%'
               OR (c.claim_reference NOT LIKE 'DUP-%' AND c.claim_reference NOT REGEXP '^CLM-[0-9]{4}-[0-9]{7}$')
        """,
        anomaly_codes=["E065"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E066",
        rule_name="CARC Adjustment Reason Code Standard Conformance",
        category_code="VALIDITY",
        category_id=2,
        dimension_code="Validity",
        default_severity_code="Low",
        target_table="adjustments",
        target_column="reason_code",
        description="Validates that financial adjustment reason codes adhere to standard CARC naming conventions.",
        sql_logic="""
            SELECT a.adjustment_id, a.claim_id, a.reason_code, c.claim_reference
            FROM adjustments a
            JOIN claims c ON a.claim_id = c.claim_id
            WHERE a.reason_code = 'NONSTD99'
               OR a.reason_code NOT IN ('CO-45', 'CO-97', 'PR-1', 'PR-2', 'PR-3', 'OA-23', 'PI-100', 'CR-1')
        """,
        anomaly_codes=["E066"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E067",
        rule_name="Facility Federal Taxpayer ID (TIN) Format Conformance",
        category_code="VALIDITY",
        category_id=2,
        dimension_code="Validity",
        default_severity_code="Low",
        target_table="facilities",
        target_column="tin",
        description="Validates that healthcare facility TINs conform to the standard 9-digit 'XX-XXXXXXX' syntax.",
        sql_logic="""
            SELECT f.facility_id, f.facility_reference, f.tin
            FROM facilities f
            WHERE f.tin = '00-XXXXX'
               OR f.tin NOT REGEXP '^[0-9]{2}-[0-9]{7}$'
        """,
        anomaly_codes=["E067"],
        detection_method="SQL_SET",
    ),
]


def evaluate_formatting_rule(conn: pymysql.Connection, rule: QARuleDefinition) -> Tuple[int, List[QADetectionRecord]]:
    """Execute a formatting & syntax rule (via SQL or Python Luhn validator) and collect detection findings."""
    detections: List[QADetectionRecord] = []

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total_count FROM {rule.target_table}")
        records_evaluated = cur.fetchone()["total_count"]

        if rule.detection_method == "PYTHON_VALIDATION" and rule.rule_code == "R-E061":
            # Python CMS Luhn Checksum validation over providers
            cur.execute(rule.sql_logic)
            rows = cur.fetchall()
            for r in rows:
                npi_val = str(r["npi"])
                if not validate_npi(npi_val):
                    det = QADetectionRecord(
                        rule_code=rule.rule_code,
                        anomaly_code=rule.anomaly_codes[0],
                        target_table=rule.target_table,
                        target_record_id=r["provider_id"],
                        target_business_reference=r["provider_reference"],
                        target_column=rule.target_column,
                        detected_value=npi_val,
                        severity_code=rule.default_severity_code,
                        dimension_code=rule.dimension_code,
                        explanation=f"Provider NPI ({npi_val}) failed CMS Luhn checksum algorithm",
                    )
                    detections.append(det)
        else:
            cur.execute(rule.sql_logic)
            rows = cur.fetchall()

            for r in rows:
                pk_col = f"{rule.target_table[:-1] if rule.target_table.endswith('s') else rule.target_table}_id"
                if rule.target_table == "claim_lines":
                    pk_col = "claim_line_id"
                elif rule.target_table == "encounter_diagnoses":
                    pk_col = "diagnosis_id"

                record_id = r.get(pk_col, 0)
                biz_ref = r.get("claim_reference") or r.get("provider_reference") or r.get("facility_reference") or f"{rule.target_table.upper()}-{record_id}"

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
                    explanation=f"{rule.rule_name}: invalid code syntax on {rule.target_table} ID {record_id} ({r.get(rule.target_column)})",
                    claim_id=claim_id,
                )
                detections.append(det)

    return records_evaluated, detections

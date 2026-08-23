"""Completeness Anomaly Mutators (E001–E010)."""

from typing import List, Dict, Any
import pymysql
from generator.random_state import GeneratorRandomState
from generator.injector.models import GroundTruthRecord
from generator.injector.taxonomy import TAXONOMY


def mutate_completeness(
    conn: pymysql.Connection,
    anomaly_code: str,
    count: int,
    rng: GeneratorRandomState,
    profile_name: str,
    seed: int,
    dry_run: bool = False,
) -> List[GroundTruthRecord]:
    """Execute completeness mutations (E001–E010)."""
    defn = TAXONOMY[anomaly_code]
    records: List[GroundTruthRecord] = []

    with conn.cursor() as cur:
        if anomaly_code == "E001":
            cur.execute("SELECT patient_id, patient_reference, address_state FROM patients WHERE address_state != '' ORDER BY patient_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="patients",
                    target_record_id=row["patient_id"],
                    target_business_reference=row["patient_reference"],
                    target_column="address_state",
                    original_value=row["address_state"],
                    mutated_value="",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE patients SET address_state = '' WHERE patient_id = %s", (row["patient_id"],))
                records.append(rec)

        elif anomaly_code == "E002":
            cur.execute("SELECT provider_id, provider_reference, facility_id FROM providers WHERE facility_id IS NOT NULL ORDER BY provider_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="providers",
                    target_record_id=row["provider_id"],
                    target_business_reference=row["provider_reference"],
                    target_column="facility_id",
                    original_value=str(row["facility_id"]),
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE providers SET facility_id = NULL WHERE provider_id = %s", (row["provider_id"],))
                records.append(rec)

        elif anomaly_code == "E003":
            cur.execute("SELECT coverage_id, member_id, group_number FROM patient_coverage WHERE group_number IS NOT NULL ORDER BY coverage_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="patient_coverage",
                    target_record_id=row["coverage_id"],
                    target_business_reference=row["member_id"],
                    target_column="group_number",
                    original_value=row["group_number"],
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE patient_coverage SET group_number = NULL WHERE coverage_id = %s", (row["coverage_id"],))
                records.append(rec)

        elif anomaly_code == "E004":
            cur.execute("SELECT claim_line_id, claim_id, procedure_description FROM claim_lines WHERE procedure_description IS NOT NULL ORDER BY claim_line_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_lines",
                    target_record_id=row["claim_line_id"],
                    target_business_reference=f"LINE-{row['claim_line_id']}",
                    target_column="procedure_description",
                    original_value=row["procedure_description"],
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE claim_lines SET procedure_description = NULL WHERE claim_line_id = %s", (row["claim_line_id"],))
                records.append(rec)

        elif anomaly_code == "E005":
            cur.execute("SELECT encounter_id, encounter_reference, discharge_date FROM encounters WHERE discharge_date IS NOT NULL AND encounter_type = 'Inpatient Hospital' ORDER BY encounter_id")
            rows = cur.fetchall()
            if not rows:
                cur.execute("SELECT encounter_id, encounter_reference, discharge_date FROM encounters WHERE discharge_date IS NOT NULL ORDER BY encounter_id")
                rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="encounters",
                    target_record_id=row["encounter_id"],
                    target_business_reference=row["encounter_reference"],
                    target_column="discharge_date",
                    original_value=str(row["discharge_date"]),
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE encounters SET discharge_date = NULL WHERE encounter_id = %s", (row["encounter_id"],))
                records.append(rec)

        elif anomaly_code == "E006":
            cur.execute("SELECT claim_id, claim_reference, adjudication_date FROM claims WHERE current_status_code IN ('Paid', 'Partially Paid') AND adjudication_date IS NOT NULL ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="adjudication_date",
                    original_value=str(row["adjudication_date"]),
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE claims SET adjudication_date = NULL WHERE claim_id = %s", (row["claim_id"],))
                records.append(rec)

        elif anomaly_code == "E007":
            cur.execute("SELECT adjustment_id, claim_id, adjustment_description FROM adjustments WHERE adjustment_description IS NOT NULL ORDER BY adjustment_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="adjustments",
                    target_record_id=row["adjustment_id"],
                    target_business_reference=f"ADJ-{row['adjustment_id']}",
                    target_column="adjustment_description",
                    original_value=row["adjustment_description"],
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE adjustments SET adjustment_description = NULL WHERE adjustment_id = %s", (row["adjustment_id"],))
                records.append(rec)

        elif anomaly_code == "E008":
            cur.execute("SELECT history_id, claim_id, transition_reason FROM claim_status_history WHERE transition_reason IS NOT NULL ORDER BY history_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_status_history",
                    target_record_id=row["history_id"],
                    target_business_reference=f"CSH-{row['history_id']}",
                    target_column="transition_reason",
                    original_value=row["transition_reason"],
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE claim_status_history SET transition_reason = NULL WHERE history_id = %s", (row["history_id"],))
                records.append(rec)

        elif anomaly_code == "E009":
            cur.execute("SELECT coverage_id, member_id, termination_date FROM patient_coverage WHERE termination_date IS NOT NULL ORDER BY coverage_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="patient_coverage",
                    target_record_id=row["coverage_id"],
                    target_business_reference=row["member_id"],
                    target_column="termination_date",
                    original_value=str(row["termination_date"]),
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE patient_coverage SET termination_date = NULL WHERE coverage_id = %s", (row["coverage_id"],))
                records.append(rec)

        elif anomaly_code == "E010":
            cur.execute("SELECT diagnosis_id, encounter_id, diagnosis_description FROM encounter_diagnoses WHERE is_primary = 0 ORDER BY diagnosis_id")
            rows = cur.fetchall()
            if not rows:
                cur.execute("SELECT diagnosis_id, encounter_id, diagnosis_description FROM encounter_diagnoses ORDER BY diagnosis_id")
                rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="encounter_diagnoses",
                    target_record_id=row["diagnosis_id"],
                    target_business_reference=f"DIAG-{row['diagnosis_id']}",
                    target_column="diagnosis_description",
                    original_value=row["diagnosis_description"],
                    mutated_value=None,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=defn.description,
                    expected_rule_category=defn.expected_rule_category,
                )
                if not dry_run:
                    cur.execute("UPDATE encounter_diagnoses SET diagnosis_description = NULL WHERE diagnosis_id = %s", (row["diagnosis_id"],))
                records.append(rec)

    return records

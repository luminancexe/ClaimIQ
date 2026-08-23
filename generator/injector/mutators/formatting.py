"""Code & Formatting Anomaly Mutators (E061–E067)."""

from typing import List, Dict, Any
import pymysql
from generator.random_state import GeneratorRandomState
from generator.identifiers import validate_npi
from generator.injector.models import GroundTruthRecord
from generator.injector.taxonomy import TAXONOMY


def mutate_formatting(
    conn: pymysql.Connection,
    anomaly_code: str,
    count: int,
    rng: GeneratorRandomState,
    profile_name: str,
    seed: int,
    dry_run: bool = False,
) -> List[GroundTruthRecord]:
    """Execute formatting & code validity mutations (E061–E067)."""
    defn = TAXONOMY[anomaly_code]
    records: List[GroundTruthRecord] = []

    with conn.cursor() as cur:
        if anomaly_code == "E061":
            # Invalid Provider NPI Checksum
            cur.execute("SELECT provider_id, provider_reference, npi FROM providers ORDER BY provider_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                # Flip the last check digit to make checksum invalid
                last_digit = int(row["npi"][-1])
                bad_digit = (last_digit + 5) % 10
                corrupted_npi = row["npi"][:-1] + str(bad_digit)
                if validate_npi(corrupted_npi):
                    corrupted_npi = row["npi"][:-1] + str((bad_digit + 1) % 10)

                if not dry_run:
                    cur.execute("UPDATE providers SET npi = %s WHERE provider_id = %s", (corrupted_npi, row["provider_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="providers",
                    target_record_id=row["provider_id"],
                    target_business_reference=row["provider_reference"],
                    target_column="npi",
                    original_value=row["npi"],
                    mutated_value=corrupted_npi,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Provider NPI corrupted to {corrupted_npi} failing CMS Luhn checksum algorithm",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E062":
            # Malformed CPT Procedure Code
            cur.execute("SELECT claim_line_id, claim_id, cpt_code FROM claim_lines ORDER BY claim_line_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                bad_cpt = "CPT99X"
                if not dry_run:
                    cur.execute("UPDATE claim_lines SET cpt_code = %s WHERE claim_line_id = %s", (bad_cpt, row["claim_line_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_lines",
                    target_record_id=row["claim_line_id"],
                    target_business_reference=f"LINE-{row['claim_line_id']}",
                    target_column="cpt_code",
                    original_value=row["cpt_code"],
                    mutated_value=bad_cpt,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim line CPT code set to malformed value ({bad_cpt})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E063":
            # Malformed ICD-10 Diagnosis Code
            cur.execute("SELECT diagnosis_id, encounter_id, icd10_code FROM encounter_diagnoses ORDER BY diagnosis_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                bad_icd = "ICD9999"
                if not dry_run:
                    cur.execute("UPDATE encounter_diagnoses SET icd10_code = %s WHERE diagnosis_id = %s", (bad_icd, row["diagnosis_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="encounter_diagnoses",
                    target_record_id=row["diagnosis_id"],
                    target_business_reference=f"DIAG-{row['diagnosis_id']}",
                    target_column="icd10_code",
                    original_value=row["icd10_code"],
                    mutated_value=bad_icd,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Encounter ICD-10 code set to malformed value ({bad_icd})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E064":
            # Malformed NUCC Taxonomy Code
            cur.execute("SELECT provider_id, provider_reference, taxonomy_code FROM providers ORDER BY provider_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                bad_tax = "TAX-999"
                if not dry_run:
                    cur.execute("UPDATE providers SET taxonomy_code = %s WHERE provider_id = %s", (bad_tax, row["provider_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="providers",
                    target_record_id=row["provider_id"],
                    target_business_reference=row["provider_reference"],
                    target_column="taxonomy_code",
                    original_value=row["taxonomy_code"],
                    mutated_value=bad_tax,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Provider taxonomy code set to non-standard syntax ({bad_tax})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E065":
            # Malformed Business Reference Format
            cur.execute("SELECT claim_id, claim_reference FROM claims ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                bad_ref = f"BAD-REF-{row['claim_id']}"
                if not dry_run:
                    cur.execute("UPDATE claims SET claim_reference = %s WHERE claim_id = %s", (bad_ref, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=bad_ref,
                    target_column="claim_reference",
                    original_value=row["claim_reference"],
                    mutated_value=bad_ref,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim business reference mutated to non-conforming format ({bad_ref})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E066":
            # Invalid Adjustment Reason Code
            cur.execute("SELECT adjustment_id, claim_id, reason_code FROM adjustments ORDER BY adjustment_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                bad_rc = "NONSTD99"
                if not dry_run:
                    cur.execute("UPDATE adjustments SET reason_code = %s WHERE adjustment_id = %s", (bad_rc, row["adjustment_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="adjustments",
                    target_record_id=row["adjustment_id"],
                    target_business_reference=f"ADJ-{row['adjustment_id']}",
                    target_column="reason_code",
                    original_value=row["reason_code"],
                    mutated_value=bad_rc,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Adjustment reason code mutated to non-standard code ({bad_rc})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E067":
            # Malformed Facility TIN Format
            cur.execute("SELECT facility_id, facility_reference, tin FROM facilities ORDER BY facility_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                bad_tin = "00-XXXXX"
                if not dry_run:
                    cur.execute("UPDATE facilities SET tin = %s WHERE facility_id = %s", (bad_tin, row["facility_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="facilities",
                    target_record_id=row["facility_id"],
                    target_business_reference=row["facility_reference"],
                    target_column="tin",
                    original_value=row["tin"],
                    mutated_value=bad_tin,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Facility Federal Tax ID (TIN) mutated to non-standard format ({bad_tin})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

    return records

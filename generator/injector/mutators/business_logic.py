"""Business Logic & Operational Anomaly Mutators (E051–E060)."""

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import pymysql
from generator.random_state import GeneratorRandomState
from generator.injector.models import GroundTruthRecord
from generator.injector.taxonomy import TAXONOMY


def mutate_business_logic(
    conn: pymysql.Connection,
    anomaly_code: str,
    count: int,
    rng: GeneratorRandomState,
    profile_name: str,
    seed: int,
    dry_run: bool = False,
) -> List[GroundTruthRecord]:
    """Execute business logic & operational mutations (E051–E060)."""
    defn = TAXONOMY[anomaly_code]
    records: List[GroundTruthRecord] = []

    with conn.cursor() as cur:
        if anomaly_code == "E051":
            # Claim without service lines (delete lines for claim)
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.total_billed_amount
                FROM claims c
                JOIN claim_lines cl ON c.claim_id = cl.claim_id
                WHERE c.total_billed_amount > 0.00
                GROUP BY c.claim_id, c.claim_reference, c.total_billed_amount
                ORDER BY c.claim_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("DELETE FROM claim_lines WHERE claim_id = %s", (row["claim_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_lines",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="claim_id",
                    original_value=f"HAS_LINES_FOR_CLAIM_{row['claim_id']}",
                    mutated_value="ZERO_LINES",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"All service lines purged for positive-billed claim {row['claim_reference']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E052":
            # Claim patient differs from encounter patient
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.patient_id, e.encounter_id, e.patient_id AS enc_pat_id
                FROM claims c
                JOIN encounters e ON c.encounter_id = e.encounter_id
                ORDER BY c.claim_id
            """)
            rows = cur.fetchall()
            cur.execute("SELECT patient_id FROM patients ORDER BY patient_id")
            all_patients = [r["patient_id"] for r in cur.fetchall()]
            if not rows or len(all_patients) < 2:
                return records

            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                other_pats = [p for p in all_patients if p != row["enc_pat_id"]]
                new_pat = rng.choice(other_pats) if other_pats else all_patients[0]
                if not dry_run:
                    cur.execute("UPDATE claims SET patient_id = %s WHERE claim_id = %s", (new_pat, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="patient_id",
                    original_value=str(row["patient_id"]),
                    mutated_value=str(new_pat),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim patient changed to {new_pat} mismatching encounter patient {row['enc_pat_id']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E053":
            # Claim provider differs from encounter provider
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.billing_provider_id, e.provider_id AS enc_prov_id
                FROM claims c
                JOIN encounters e ON c.encounter_id = e.encounter_id
                ORDER BY c.claim_id
            """)
            rows = cur.fetchall()
            cur.execute("SELECT provider_id FROM providers ORDER BY provider_id")
            all_provs = [r["provider_id"] for r in cur.fetchall()]
            if not rows or len(all_provs) < 2:
                return records

            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                other_provs = [p for p in all_provs if p != row["enc_prov_id"]]
                new_prov = rng.choice(other_provs) if other_provs else all_provs[0]
                if not dry_run:
                    cur.execute("UPDATE claims SET billing_provider_id = %s WHERE claim_id = %s", (new_prov, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="billing_provider_id",
                    original_value=str(row["billing_provider_id"]),
                    mutated_value=str(new_prov),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim billing provider changed to {new_prov} mismatching encounter clinician {row['enc_prov_id']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E054":
            # Claim submitted outside timely filing limit
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.submission_date, e.date_of_service, p.timely_filing_days
                FROM claims c
                JOIN encounters e ON c.encounter_id = e.encounter_id
                JOIN payers p ON c.payer_id = p.payer_id
                ORDER BY c.claim_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                late_sub = row["date_of_service"] + timedelta(days=row["timely_filing_days"] + 60)
                if not dry_run:
                    cur.execute("UPDATE claims SET submission_date = %s WHERE claim_id = %s", (late_sub, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="submission_date",
                    original_value=str(row["submission_date"]),
                    mutated_value=str(late_sub),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim submission date set to {late_sub} exceeding {row['timely_filing_days']}-day timely filing limit",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E055":
            # Payment exists for incompatible claim status (Submitted)
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.current_status_code
                FROM claims c
                JOIN payments p ON c.claim_id = p.claim_id
                WHERE c.current_status_code = 'Paid' AND p.paid_amount > 0.00
                ORDER BY c.claim_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("UPDATE claims SET current_status_code = 'Submitted' WHERE claim_id = %s", (row["claim_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="current_status_code",
                    original_value="Paid",
                    mutated_value="Submitted",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Claim status reverted to Submitted while keeping positive cash payment records",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E056":
            # Denial record attached to paid claim
            cur.execute("SELECT claim_id, claim_reference FROM claims WHERE current_status_code = 'Paid' ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_den_id = None
                if not dry_run:
                    cur.execute("""
                        INSERT INTO denials (claim_id, denial_code, denial_reason, denial_date, is_appealable)
                        VALUES (%s, 'CO-16', 'Claim lacks information or has submission errors', CURDATE(), 1)
                    """, (row["claim_id"],))
                    new_den_id = cur.lastrowid

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="denials",
                    target_record_id=new_den_id if new_den_id else row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="claim_id",
                    original_value="NEW_RECORD",
                    mutated_value=f"DENIAL_ON_PAID_CLAIM_{row['claim_id']}",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Contradictory denial record attached to fully Paid claim {row['claim_reference']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E057":
            # Reconciliation marked balanced despite variance
            cur.execute("""
                SELECT reconciliation_id, claim_id, variance_amount, reconciliation_status
                FROM reconciliations
                WHERE reconciliation_status = 'BALANCED'
                ORDER BY reconciliation_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_var = Decimal("250.00")
                if not dry_run:
                    cur.execute("UPDATE reconciliations SET variance_amount = %s WHERE reconciliation_id = %s", (new_var, row["reconciliation_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="reconciliations",
                    target_record_id=row["reconciliation_id"],
                    target_business_reference=f"REC-CLAIM-{row['claim_id']}",
                    target_column="variance_amount",
                    original_value="0.00",
                    mutated_value=str(new_var),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Reconciliation left marked BALANCED despite variance = {new_var}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E058":
            # Reconciliation marked unbalanced despite zero variance
            cur.execute("""
                SELECT reconciliation_id, claim_id, variance_amount, reconciliation_status
                FROM reconciliations
                WHERE reconciliation_status = 'BALANCED' AND variance_amount = 0.00
                ORDER BY reconciliation_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("UPDATE reconciliations SET reconciliation_status = 'UNBALANCED' WHERE reconciliation_id = %s", (row["reconciliation_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="reconciliations",
                    target_record_id=row["reconciliation_id"],
                    target_business_reference=f"REC-CLAIM-{row['claim_id']}",
                    target_column="reconciliation_status",
                    original_value="BALANCED",
                    mutated_value="UNBALANCED",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Reconciliation erroneously marked UNBALANCED when variance = 0.00",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E059":
            # Patient coverage outside service date
            cur.execute("""
                SELECT pc.coverage_id, pc.patient_id, pc.member_id, pc.effective_date, e.date_of_service
                FROM patient_coverage pc
                JOIN encounters e ON pc.patient_id = e.patient_id
                ORDER BY pc.coverage_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_eff = row["date_of_service"] + timedelta(days=30)
                if not dry_run:
                    cur.execute("UPDATE patient_coverage SET effective_date = %s WHERE coverage_id = %s", (new_eff, row["coverage_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="patient_coverage",
                    target_record_id=row["coverage_id"],
                    target_business_reference=row["member_id"],
                    target_column="effective_date",
                    original_value=str(row["effective_date"]),
                    mutated_value=str(new_eff),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Coverage effective date set to {new_eff} after clinical DOS ({row['date_of_service']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E060":
            # Inpatient encounter with outpatient-only CPT codes
            cur.execute("""
                SELECT cl.claim_line_id, cl.claim_id, cl.cpt_code, e.encounter_type
                FROM claim_lines cl
                JOIN claims c ON cl.claim_id = c.claim_id
                JOIN encounters e ON c.encounter_id = e.encounter_id
                WHERE e.encounter_type = 'Inpatient Hospital'
                ORDER BY cl.claim_line_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("UPDATE claim_lines SET cpt_code = '99211', procedure_description = 'Office/outpatient visit, established, minimal' WHERE claim_line_id = %s", (row["claim_line_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_lines",
                    target_record_id=row["claim_line_id"],
                    target_business_reference=f"LINE-{row['claim_line_id']}",
                    target_column="cpt_code",
                    original_value=row["cpt_code"],
                    mutated_value="99211",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Inpatient hospitalization line replaced with minor outpatient evaluation code (99211)",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

    return records

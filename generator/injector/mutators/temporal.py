"""Temporal & Chronological Anomaly Mutators (E034–E042)."""

from datetime import date, timedelta
from typing import List, Dict, Any
import pymysql
from generator.random_state import GeneratorRandomState
from generator.injector.models import GroundTruthRecord
from generator.injector.taxonomy import TAXONOMY


def mutate_temporal(
    conn: pymysql.Connection,
    anomaly_code: str,
    count: int,
    rng: GeneratorRandomState,
    profile_name: str,
    seed: int,
    dry_run: bool = False,
) -> List[GroundTruthRecord]:
    """Execute temporal mutations (E034–E042)."""
    defn = TAXONOMY[anomaly_code]
    records: List[GroundTruthRecord] = []

    with conn.cursor() as cur:
        if anomaly_code == "E034":
            # Date of service after submission date
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.submission_date, e.encounter_id, e.date_of_service
                FROM claims c
                JOIN encounters e ON c.encounter_id = e.encounter_id
                ORDER BY c.claim_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mutated_dos = row["submission_date"] + timedelta(days=15)
                if not dry_run:
                    cur.execute("UPDATE encounters SET date_of_service = %s WHERE encounter_id = %s", (mutated_dos, row["encounter_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="encounters",
                    target_record_id=row["encounter_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="date_of_service",
                    original_value=str(row["date_of_service"]),
                    mutated_value=str(mutated_dos),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Encounter DOS set to {mutated_dos} which is after claim submission ({row['submission_date']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E035":
            # Submission date after adjudication date
            cur.execute("SELECT claim_id, claim_reference, submission_date, adjudication_date FROM claims WHERE adjudication_date IS NOT NULL ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mutated_sub = row["adjudication_date"] + timedelta(days=10)
                if not dry_run:
                    cur.execute("UPDATE claims SET submission_date = %s WHERE claim_id = %s", (mutated_sub, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="submission_date",
                    original_value=str(row["submission_date"]),
                    mutated_value=str(mutated_sub),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Submission date set to {mutated_sub} which is after adjudication date ({row['adjudication_date']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E036":
            # Payment date before submission date
            cur.execute("""
                SELECT p.payment_id, p.payment_reference, p.payment_date, c.claim_id, c.submission_date
                FROM payments p
                JOIN claims c ON p.claim_id = c.claim_id
                ORDER BY p.payment_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mutated_pmt = row["submission_date"] - timedelta(days=5)
                if not dry_run:
                    cur.execute("UPDATE payments SET payment_date = %s WHERE payment_id = %s", (mutated_pmt, row["payment_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="payments",
                    target_record_id=row["payment_id"],
                    target_business_reference=row["payment_reference"],
                    target_column="payment_date",
                    original_value=str(row["payment_date"]),
                    mutated_value=str(mutated_pmt),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Payment date set to {mutated_pmt} which precedes claim submission ({row['submission_date']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E037":
            # Payment date before adjudication date
            cur.execute("""
                SELECT p.payment_id, p.payment_reference, p.payment_date, c.claim_id, c.adjudication_date
                FROM payments p
                JOIN claims c ON p.claim_id = c.claim_id
                WHERE c.adjudication_date IS NOT NULL
                ORDER BY p.payment_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mutated_pmt = row["adjudication_date"] - timedelta(days=3)
                if not dry_run:
                    cur.execute("UPDATE payments SET payment_date = %s WHERE payment_id = %s", (mutated_pmt, row["payment_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="payments",
                    target_record_id=row["payment_id"],
                    target_business_reference=row["payment_reference"],
                    target_column="payment_date",
                    original_value=str(row["payment_date"]),
                    mutated_value=str(mutated_pmt),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Payment date set to {mutated_pmt} which precedes adjudication ({row['adjudication_date']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E038":
            # Remittance date before adjudication date
            cur.execute("""
                SELECT r.remittance_id, r.remittance_reference, r.remittance_date, c.adjudication_date
                FROM remittances r
                JOIN payments p ON r.remittance_id = p.remittance_id
                JOIN claims c ON p.claim_id = c.claim_id
                WHERE c.adjudication_date IS NOT NULL
                ORDER BY r.remittance_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mutated_remit = row["adjudication_date"] - timedelta(days=4)
                if not dry_run:
                    cur.execute("UPDATE remittances SET remittance_date = %s WHERE remittance_id = %s", (mutated_remit, row["remittance_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="remittances",
                    target_record_id=row["remittance_id"],
                    target_business_reference=row["remittance_reference"],
                    target_column="remittance_date",
                    original_value=str(row["remittance_date"]),
                    mutated_value=str(mutated_remit),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Remittance date set to {mutated_remit} preceding adjudication ({row['adjudication_date']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E039":
            # Denial date before submission date
            cur.execute("""
                SELECT d.denial_id, d.denial_date, c.claim_id, c.claim_reference, c.submission_date
                FROM denials d
                JOIN claims c ON d.claim_id = c.claim_id
                ORDER BY d.denial_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mutated_denial = row["submission_date"] - timedelta(days=7)
                if not dry_run:
                    cur.execute("UPDATE denials SET denial_date = %s WHERE denial_id = %s", (mutated_denial, row["denial_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="denials",
                    target_record_id=row["denial_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="denial_date",
                    original_value=str(row["denial_date"]),
                    mutated_value=str(mutated_denial),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Denial date set to {mutated_denial} which precedes submission ({row['submission_date']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E040":
            # Encounter discharge date before date of service
            cur.execute("""
                SELECT encounter_id, encounter_reference, date_of_service, discharge_date
                FROM encounters
                WHERE discharge_date IS NOT NULL
                ORDER BY encounter_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mutated_dis = row["date_of_service"] - timedelta(days=2)
                if not dry_run:
                    cur.execute("UPDATE encounters SET discharge_date = %s WHERE encounter_id = %s", (mutated_dis, row["encounter_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="encounters",
                    target_record_id=row["encounter_id"],
                    target_business_reference=row["encounter_reference"],
                    target_column="discharge_date",
                    original_value=str(row["discharge_date"]),
                    mutated_value=str(mutated_dis),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Discharge date set to {mutated_dis} preceding admission DOS ({row['date_of_service']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E041":
            # Future-dated claim submission event
            cur.execute("SELECT claim_id, claim_reference, submission_date FROM claims ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                future_date = date(2028, 12, 31)
                if not dry_run:
                    cur.execute("UPDATE claims SET submission_date = %s WHERE claim_id = %s", (future_date, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="submission_date",
                    original_value=str(row["submission_date"]),
                    mutated_value=str(future_date),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim submission date set to future date {future_date}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E042":
            # Claim submission precedes patient date of birth
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.submission_date, p.patient_id, p.date_of_birth
                FROM claims c
                JOIN patients p ON c.patient_id = p.patient_id
                ORDER BY c.claim_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                pre_dob = row["date_of_birth"] - timedelta(days=365)
                if not dry_run:
                    cur.execute("UPDATE claims SET submission_date = %s WHERE claim_id = %s", (pre_dob, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="submission_date",
                    original_value=str(row["submission_date"]),
                    mutated_value=str(pre_dob),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Submission date set to {pre_dob} preceding patient DOB ({row['date_of_birth']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

    return records

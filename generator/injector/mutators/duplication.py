"""Duplication Anomaly Mutators (E011–E015)."""

from typing import List, Dict, Any
import pymysql
from generator.random_state import GeneratorRandomState
from generator.injector.models import GroundTruthRecord
from generator.injector.taxonomy import TAXONOMY


def mutate_duplication(
    conn: pymysql.Connection,
    anomaly_code: str,
    count: int,
    rng: GeneratorRandomState,
    profile_name: str,
    seed: int,
    dry_run: bool = False,
) -> List[GroundTruthRecord]:
    """Execute duplication mutations (E011–E015)."""
    defn = TAXONOMY[anomaly_code]
    records: List[GroundTruthRecord] = []

    with conn.cursor() as cur:
        if anomaly_code == "E011":
            # E011: Duplicate Claim
            cur.execute("""
                SELECT claim_id, claim_reference, encounter_id, patient_id, billing_provider_id,
                       payer_id, current_status_code, total_billed_amount, submission_date,
                       adjudication_date, is_reconciled
                FROM claims
                ORDER BY claim_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_claim_ref = f"DUP-{row['claim_reference']}"
                new_claim_id = None
                if not dry_run:
                    cur.execute("""
                        INSERT INTO claims (claim_reference, encounter_id, patient_id, billing_provider_id,
                                            payer_id, current_status_code, total_billed_amount, submission_date,
                                            adjudication_date, is_reconciled)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        new_claim_ref, row["encounter_id"], row["patient_id"], row["billing_provider_id"],
                        row["payer_id"], row["current_status_code"], row["total_billed_amount"], row["submission_date"],
                        row["adjudication_date"], row["is_reconciled"]
                    ))
                    new_claim_id = cur.lastrowid
                
                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=new_claim_id if new_claim_id else row["claim_id"],
                    target_business_reference=new_claim_ref,
                    target_column="claim_reference",
                    original_value="NEW_RECORD",
                    mutated_value=f"CLONE_OF_CLAIM_{row['claim_id']}",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Duplicate claim created cloning claim {row['claim_reference']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E012":
            # E012: Duplicate Claim Line
            cur.execute("""
                SELECT cl.claim_line_id, cl.claim_id, cl.line_number, cl.cpt_code,
                       cl.procedure_description, cl.units, cl.unit_price, cl.line_billed_amount, cl.line_status
                FROM claim_lines cl
                ORDER BY cl.claim_line_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_line_id = None
                if not dry_run:
                    cur.execute("SELECT MAX(line_number) AS max_line FROM claim_lines WHERE claim_id = %s", (row["claim_id"],))
                    max_line = (cur.fetchone()["max_line"] or 1) + 1
                    cur.execute("""
                        INSERT INTO claim_lines (claim_id, line_number, cpt_code, procedure_description,
                                                units, unit_price, line_billed_amount, line_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row["claim_id"], max_line, row["cpt_code"], row["procedure_description"],
                        row["units"], row["unit_price"], row["line_billed_amount"], row["line_status"]
                    ))
                    new_line_id = cur.lastrowid

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_lines",
                    target_record_id=new_line_id if new_line_id else row["claim_line_id"],
                    target_business_reference=f"LINE-{new_line_id if new_line_id else row['claim_line_id']}",
                    target_column="cpt_code",
                    original_value="NEW_RECORD",
                    mutated_value=f"CLONE_OF_LINE_{row['claim_line_id']}",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Duplicate service line ({row['cpt_code']}) inserted into claim {row['claim_id']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E013":
            # E013: Duplicate Payment
            cur.execute("""
                SELECT payment_id, payment_reference, remittance_id, claim_id, paid_amount, payment_date
                FROM payments
                ORDER BY payment_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_pmt_ref = f"DUP-{row['payment_reference']}"
                new_pmt_id = None
                if not dry_run:
                    cur.execute("""
                        INSERT INTO payments (payment_reference, remittance_id, claim_id, paid_amount, payment_date)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        new_pmt_ref, row["remittance_id"], row["claim_id"], row["paid_amount"], row["payment_date"]
                    ))
                    new_pmt_id = cur.lastrowid

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="payments",
                    target_record_id=new_pmt_id if new_pmt_id else row["payment_id"],
                    target_business_reference=new_pmt_ref,
                    target_column="paid_amount",
                    original_value="NEW_RECORD",
                    mutated_value=f"CLONE_OF_PMT_{row['payment_id']}",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Duplicate payment transaction created for claim {row['claim_id']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E014":
            # E014: Duplicate Remittance Trace
            cur.execute("SELECT remittance_id, remittance_reference, check_trace_number FROM remittances ORDER BY remittance_id")
            rows = cur.fetchall()
            if len(rows) < 2:
                return records
            selected = rng.sample(rows[1:], min(count, len(rows) - 1))
            source_trace = rows[0]["check_trace_number"]
            for row in selected:
                # Append duplicate indicator to create logical duplicate without violating MySQL unique index
                dup_trace = f"{source_trace}-DUP"
                if not dry_run:
                    cur.execute("UPDATE remittances SET check_trace_number = %s WHERE remittance_id = %s", (dup_trace, row["remittance_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="remittances",
                    target_record_id=row["remittance_id"],
                    target_business_reference=row["remittance_reference"],
                    target_column="check_trace_number",
                    original_value=row["check_trace_number"],
                    mutated_value=dup_trace,
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Logical duplicate check trace number assigned ({dup_trace})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E015":
            # E015: Duplicate Encounter
            cur.execute("""
                SELECT encounter_id, encounter_reference, patient_id, provider_id, facility_id,
                       encounter_type, date_of_service, discharge_date
                FROM encounters
                ORDER BY encounter_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_enc_ref = f"DUP-{row['encounter_reference']}"
                new_enc_id = None
                if not dry_run:
                    cur.execute("""
                        INSERT INTO encounters (encounter_reference, patient_id, provider_id, facility_id,
                                                encounter_type, date_of_service, discharge_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        new_enc_ref, row["patient_id"], row["provider_id"], row["facility_id"],
                        row["encounter_type"], row["date_of_service"], row["discharge_date"]
                    ))
                    new_enc_id = cur.lastrowid

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="encounters",
                    target_record_id=new_enc_id if new_enc_id else row["encounter_id"],
                    target_business_reference=new_enc_ref,
                    target_column="encounter_reference",
                    original_value="NEW_RECORD",
                    mutated_value=f"CLONE_OF_ENC_{row['encounter_id']}",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Duplicate clinical encounter created for patient {row['patient_id']} on {row['date_of_service']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

    return records

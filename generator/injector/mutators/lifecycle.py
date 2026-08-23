"""Claim Lifecycle & State Machine Anomaly Mutators (E043–E050)."""

from typing import List, Dict, Any
import pymysql
from generator.random_state import GeneratorRandomState
from generator.injector.models import GroundTruthRecord
from generator.injector.taxonomy import TAXONOMY


def mutate_lifecycle(
    conn: pymysql.Connection,
    anomaly_code: str,
    count: int,
    rng: GeneratorRandomState,
    profile_name: str,
    seed: int,
    dry_run: bool = False,
) -> List[GroundTruthRecord]:
    """Execute claim lifecycle mutations (E043–E050)."""
    defn = TAXONOMY[anomaly_code]
    records: List[GroundTruthRecord] = []

    with conn.cursor() as cur:
        if anomaly_code == "E043":
            # Invalid direct transition: Denied -> Paid
            cur.execute("SELECT claim_id, claim_reference FROM claims WHERE current_status_code = 'Paid' ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_hist_id = None
                if not dry_run:
                    cur.execute("""
                        INSERT INTO claim_status_history (claim_id, previous_status_code, new_status_code, transition_timestamp, transition_reason, actor_reference)
                        VALUES (%s, 'Denied', 'Paid', NOW(6), 'Illegal direct transition from Denied to Paid', 'INJECTOR')
                    """, (row["claim_id"],))
                    new_hist_id = cur.lastrowid

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_status_history",
                    target_record_id=new_hist_id if new_hist_id else row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="previous_status_code",
                    original_value="NEW_RECORD",
                    mutated_value="ILLEGAL_TRANSITION_DENIED_TO_PAID",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Illegal direct status transition (Denied -> Paid) inserted for claim {row['claim_reference']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E044":
            # Paid claim with zero total paid balance
            cur.execute("""
                SELECT r.reconciliation_id, r.claim_id, r.total_paid, c.claim_reference
                FROM reconciliations r
                JOIN claims c ON r.claim_id = c.claim_id
                WHERE c.current_status_code = 'Paid' AND r.total_paid > 0.00
                ORDER BY r.reconciliation_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("UPDATE reconciliations SET total_paid = 0.00 WHERE reconciliation_id = %s", (row["reconciliation_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="reconciliations",
                    target_record_id=row["reconciliation_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="total_paid",
                    original_value=str(row["total_paid"]),
                    mutated_value="0.00",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Paid claim reconciliation total_paid zeroed out",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E045":
            # Denied claim with positive payment
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
                    cur.execute("UPDATE claims SET current_status_code = 'Denied' WHERE claim_id = %s", (row["claim_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="current_status_code",
                    original_value="Paid",
                    mutated_value="Denied",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Claim with active cash disbursements mutated to Denied status",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E046":
            # Rejected claim with payment allocation
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
                    cur.execute("UPDATE claims SET current_status_code = 'Rejected' WHERE claim_id = %s", (row["claim_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="current_status_code",
                    original_value="Paid",
                    mutated_value="Rejected",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Claim with payment disbursements mutated to Rejected status",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E047":
            # Pending claim with finalized payment
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
                    cur.execute("UPDATE claims SET current_status_code = 'Pending' WHERE claim_id = %s", (row["claim_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="current_status_code",
                    original_value="Paid",
                    mutated_value="Pending",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Claim with finalized payment mutated to in-flight Pending review status",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E048":
            # Submitted claim marked reconciled
            cur.execute("SELECT claim_id, claim_reference, is_reconciled FROM claims WHERE current_status_code = 'Submitted' ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                cur.execute("SELECT claim_id, claim_reference, is_reconciled FROM claims ORDER BY claim_id")
                rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("UPDATE claims SET is_reconciled = 1 WHERE claim_id = %s", (row["claim_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="is_reconciled",
                    original_value=str(row["is_reconciled"]),
                    mutated_value="1",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Unadjudicated claim prematurely flagged as is_reconciled = 1",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E049":
            # Paid claim missing adjudication date
            cur.execute("SELECT claim_id, claim_reference, adjudication_date FROM claims WHERE current_status_code = 'Paid' AND adjudication_date IS NOT NULL ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("UPDATE claims SET adjudication_date = NULL WHERE claim_id = %s", (row["claim_id"],))

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
                    description="Paid claim adjudication_date cleared to NULL",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E050":
            # Duplicate final status transitions
            cur.execute("SELECT history_id, claim_id, new_status_code FROM claim_status_history WHERE new_status_code = 'Paid' ORDER BY history_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_hist_id = None
                if not dry_run:
                    cur.execute("""
                        INSERT INTO claim_status_history (claim_id, previous_status_code, new_status_code, transition_timestamp, transition_reason, actor_reference)
                        VALUES (%s, 'Paid', 'Paid', NOW(6), 'Redundant duplicate Paid status logged', 'INJECTOR')
                    """, (row["claim_id"],))
                    new_hist_id = cur.lastrowid

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_status_history",
                    target_record_id=new_hist_id if new_hist_id else row["history_id"],
                    target_business_reference=f"CLAIM-{row['claim_id']}",
                    target_column="new_status_code",
                    original_value="NEW_RECORD",
                    mutated_value="DUPLICATE_PAID_TRANSITION",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Duplicate consecutive Paid transition logged for claim {row['claim_id']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

    return records

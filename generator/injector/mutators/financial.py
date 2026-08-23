"""Financial & Reconciliation Anomaly Mutators (E023–E033)."""

from decimal import Decimal
from typing import List, Dict, Any
import pymysql
from generator.random_state import GeneratorRandomState
from generator.injector.models import GroundTruthRecord
from generator.injector.taxonomy import TAXONOMY


def mutate_financial(
    conn: pymysql.Connection,
    anomaly_code: str,
    count: int,
    rng: GeneratorRandomState,
    profile_name: str,
    seed: int,
    dry_run: bool = False,
) -> List[GroundTruthRecord]:
    """Execute financial & reconciliation mutations (E023–E033)."""
    defn = TAXONOMY[anomaly_code]
    records: List[GroundTruthRecord] = []

    with conn.cursor() as cur:
        if anomaly_code == "E023":
            # Payment exceeds billed amount
            cur.execute("""
                SELECT p.payment_id, p.payment_reference, p.paid_amount, c.claim_id, c.claim_reference, c.total_billed_amount
                FROM payments p
                JOIN claims c ON p.claim_id = c.claim_id
                WHERE p.paid_amount > 0.00
                ORDER BY p.payment_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                overpay_amt = row["total_billed_amount"] + Decimal("350.00")
                if not dry_run:
                    cur.execute("UPDATE payments SET paid_amount = %s WHERE payment_id = %s", (overpay_amt, row["payment_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="payments",
                    target_record_id=row["payment_id"],
                    target_business_reference=row["payment_reference"],
                    target_column="paid_amount",
                    original_value=str(row["paid_amount"]),
                    mutated_value=str(overpay_amt),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Payment ({overpay_amt}) mutated to exceed claim billed total ({row['total_billed_amount']})",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E024":
            # Adjustment exceeds remaining balance
            cur.execute("SELECT adjustment_id, claim_id, adjustment_amount FROM adjustments WHERE adjustment_amount > 0.00 ORDER BY adjustment_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_adj = row["adjustment_amount"] + Decimal("600.00")
                if not dry_run:
                    cur.execute("UPDATE adjustments SET adjustment_amount = %s WHERE adjustment_id = %s", (new_adj, row["adjustment_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="adjustments",
                    target_record_id=row["adjustment_id"],
                    target_business_reference=f"ADJ-{row['adjustment_id']}",
                    target_column="adjustment_amount",
                    original_value=str(row["adjustment_amount"]),
                    mutated_value=str(new_adj),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Adjustment increased to {new_adj} exceeding allowable balance",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E025":
            # Inflated contractual adjustment
            cur.execute("SELECT adjustment_id, claim_id, adjustment_amount FROM adjustments WHERE group_code = 'CO' ORDER BY adjustment_id")
            rows = cur.fetchall()
            if not rows:
                cur.execute("SELECT adjustment_id, claim_id, adjustment_amount FROM adjustments ORDER BY adjustment_id")
                rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                inflated = (row["adjustment_amount"] * Decimal("2.50")).quantize(Decimal("0.01"))
                if not dry_run:
                    cur.execute("UPDATE adjustments SET adjustment_amount = %s WHERE adjustment_id = %s", (inflated, row["adjustment_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="adjustments",
                    target_record_id=row["adjustment_id"],
                    target_business_reference=f"ADJ-{row['adjustment_id']}",
                    target_column="adjustment_amount",
                    original_value=str(row["adjustment_amount"]),
                    mutated_value=str(inflated),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Contractual adjustment inflated to {inflated}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E026":
            # Incorrect patient responsibility
            cur.execute("SELECT reconciliation_id, claim_id, total_patient_resp FROM reconciliations ORDER BY reconciliation_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_resp = row["total_patient_resp"] + Decimal("150.00")
                if not dry_run:
                    cur.execute("UPDATE reconciliations SET total_patient_resp = %s WHERE reconciliation_id = %s", (new_resp, row["reconciliation_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="reconciliations",
                    target_record_id=row["reconciliation_id"],
                    target_business_reference=f"REC-CLAIM-{row['claim_id']}",
                    target_column="total_patient_resp",
                    original_value=str(row["total_patient_resp"]),
                    mutated_value=str(new_resp),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Patient responsibility increased to {new_resp} breaking balance",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E027":
            # Remittance batch total mismatch
            cur.execute("SELECT remittance_id, remittance_reference, total_paid_amount FROM remittances ORDER BY remittance_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_tot = row["total_paid_amount"] + Decimal("750.00")
                if not dry_run:
                    cur.execute("UPDATE remittances SET total_paid_amount = %s WHERE remittance_id = %s", (new_tot, row["remittance_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="remittances",
                    target_record_id=row["remittance_id"],
                    target_business_reference=row["remittance_reference"],
                    target_column="total_paid_amount",
                    original_value=str(row["total_paid_amount"]),
                    mutated_value=str(new_tot),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Remittance total altered to {new_tot} creating mismatch with child payment allocations",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E028":
            # Duplicate payment overdisbursement
            cur.execute("SELECT payment_id, payment_reference, paid_amount FROM payments WHERE paid_amount > 0.00 ORDER BY payment_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                doubled = (row["paid_amount"] * Decimal("2.00")).quantize(Decimal("0.01"))
                if not dry_run:
                    cur.execute("UPDATE payments SET paid_amount = %s WHERE payment_id = %s", (doubled, row["payment_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="payments",
                    target_record_id=row["payment_id"],
                    target_business_reference=row["payment_reference"],
                    target_column="paid_amount",
                    original_value=str(row["paid_amount"]),
                    mutated_value=str(doubled),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Payment doubled to {doubled} causing cumulative overpayment",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E029":
            # Financial reconciliation variance
            cur.execute("SELECT reconciliation_id, claim_id, variance_amount FROM reconciliations WHERE reconciliation_status = 'BALANCED' ORDER BY reconciliation_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                new_var = Decimal("235.50")
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
                    original_value=str(row["variance_amount"]),
                    mutated_value=str(new_var),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Reconciliation variance injected with {new_var}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E030":
            # Claim header billed vs line sum mismatch
            cur.execute("SELECT claim_id, claim_reference, total_billed_amount FROM claims ORDER BY claim_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mismatched = row["total_billed_amount"] + Decimal("300.00")
                if not dry_run:
                    cur.execute("UPDATE claims SET total_billed_amount = %s WHERE claim_id = %s", (mismatched, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="total_billed_amount",
                    original_value=str(row["total_billed_amount"]),
                    mutated_value=str(mismatched),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim header billed increased to {mismatched} mismatching line sums",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E031":
            # Line billed arithmetic mismatch
            cur.execute("SELECT claim_line_id, claim_id, line_billed_amount, units, unit_price FROM claim_lines ORDER BY claim_line_id")
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                mismatched = row["line_billed_amount"] + Decimal("75.00")
                if not dry_run:
                    cur.execute("UPDATE claim_lines SET line_billed_amount = %s WHERE claim_line_id = %s", (mismatched, row["claim_line_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_lines",
                    target_record_id=row["claim_line_id"],
                    target_business_reference=f"LINE-{row['claim_line_id']}",
                    target_column="line_billed_amount",
                    original_value=str(row["line_billed_amount"]),
                    mutated_value=str(mismatched),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim line billed amount set to {mismatched} != {row['units']} * {row['unit_price']}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E032":
            # Zero-billed claim with positive payment
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.total_billed_amount
                FROM claims c
                JOIN payments p ON c.claim_id = p.claim_id
                WHERE p.paid_amount > 0.00 AND c.total_billed_amount > 0.00
                ORDER BY c.claim_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("UPDATE claims SET total_billed_amount = 0.00 WHERE claim_id = %s", (row["claim_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="total_billed_amount",
                    original_value=str(row["total_billed_amount"]),
                    mutated_value="0.00",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Claim total_billed_amount set to 0.00 despite active positive cash reimbursement",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E033":
            # Paid claim with zero recorded payment
            cur.execute("""
                SELECT p.payment_id, p.payment_reference, p.paid_amount, c.claim_id, c.claim_reference
                FROM payments p
                JOIN claims c ON p.claim_id = c.claim_id
                WHERE c.current_status_code = 'Paid' AND p.paid_amount > 0.00
                ORDER BY p.payment_id
            """)
            rows = cur.fetchall()
            if not rows:
                return records
            selected = rng.sample(rows, min(count, len(rows)))
            for row in selected:
                if not dry_run:
                    cur.execute("UPDATE payments SET paid_amount = 0.00 WHERE payment_id = %s", (row["payment_id"],))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="payments",
                    target_record_id=row["payment_id"],
                    target_business_reference=row["payment_reference"],
                    target_column="paid_amount",
                    original_value=str(row["paid_amount"]),
                    mutated_value="0.00",
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description="Payment amount set to 0.00 for finalized Paid claim",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

    return records

"""Comprehensive validation suite for synthetic healthcare claims datasets."""

import pymysql
from decimal import Decimal
from typing import Dict, Any, List
from generator.identifiers import validate_npi


def validate_database_dataset(conn: pymysql.Connection) -> Dict[str, Any]:
    """Execute SQL audits against the live MySQL database to verify 100% clean baseline integrity."""
    results: Dict[str, Any] = {
        "overall_status": "PASS",
        "checks": {},
        "counts": {},
        "distributions": {},
        "errors": [],
    }

    with conn.cursor() as cursor:
        # 1. Record Counts
        tables = [
            "patients", "facilities", "providers", "payers", "insurance_plans",
            "patient_coverage", "encounters", "encounter_diagnoses", "claims",
            "claim_lines", "claim_status_history", "remittances", "payments",
            "adjustments", "denials", "reconciliations"
        ]
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM {t}")
            results["counts"][t] = cursor.fetchone()["cnt"]

        # Check A: Referential Integrity (Orphan checks)
        orphan_queries = [
            ("providers -> facilities", "SELECT COUNT(*) AS cnt FROM providers p LEFT JOIN facilities f ON p.facility_id = f.facility_id WHERE f.facility_id IS NULL AND p.facility_id IS NOT NULL"),
            ("insurance_plans -> payers", "SELECT COUNT(*) AS cnt FROM insurance_plans pl LEFT JOIN payers py ON pl.payer_id = py.payer_id WHERE py.payer_id IS NULL"),
            ("patient_coverage -> patients", "SELECT COUNT(*) AS cnt FROM patient_coverage c LEFT JOIN patients pt ON c.patient_id = pt.patient_id WHERE pt.patient_id IS NULL"),
            ("encounters -> patients", "SELECT COUNT(*) AS cnt FROM encounters e LEFT JOIN patients pt ON e.patient_id = pt.patient_id WHERE pt.patient_id IS NULL"),
            ("claims -> encounters", "SELECT COUNT(*) AS cnt FROM claims c LEFT JOIN encounters e ON c.encounter_id = e.encounter_id WHERE e.encounter_id IS NULL"),
            ("claim_lines -> claims", "SELECT COUNT(*) AS cnt FROM claim_lines cl LEFT JOIN claims c ON cl.claim_id = c.claim_id WHERE c.claim_id IS NULL"),
            ("payments -> claims", "SELECT COUNT(*) AS cnt FROM payments p LEFT JOIN claims c ON p.claim_id = c.claim_id WHERE c.claim_id IS NULL"),
            ("payments -> remittances", "SELECT COUNT(*) AS cnt FROM payments p LEFT JOIN remittances r ON p.remittance_id = r.remittance_id WHERE r.remittance_id IS NULL"),
            ("reconciliations -> claims", "SELECT COUNT(*) AS cnt FROM reconciliations rec LEFT JOIN claims c ON rec.claim_id = c.claim_id WHERE c.claim_id IS NULL"),
        ]

        ref_pass = True
        for name, query in orphan_queries:
            cursor.execute(query)
            cnt = cursor.fetchone()["cnt"]
            if cnt > 0:
                ref_pass = False
                results["errors"].append(f"Referential integrity failure: {cnt} orphaned records in {name}")
        results["checks"]["referential_integrity"] = "PASS" if ref_pass else "FAIL"

        # Check B: Uniqueness
        uq_queries = [
            ("patients.patient_reference", "SELECT patient_reference, COUNT(*) AS cnt FROM patients GROUP BY patient_reference HAVING cnt > 1"),
            ("providers.provider_reference", "SELECT provider_reference, COUNT(*) AS cnt FROM providers GROUP BY provider_reference HAVING cnt > 1"),
            ("providers.npi", "SELECT npi, COUNT(*) AS cnt FROM providers GROUP BY npi HAVING cnt > 1"),
            ("claims.claim_reference", "SELECT claim_reference, COUNT(*) AS cnt FROM claims GROUP BY claim_reference HAVING cnt > 1"),
            ("remittances.remittance_reference", "SELECT remittance_reference, COUNT(*) AS cnt FROM remittances GROUP BY remittance_reference HAVING cnt > 1"),
            ("payments.payment_reference", "SELECT payment_reference, COUNT(*) AS cnt FROM payments GROUP BY payment_reference HAVING cnt > 1"),
        ]
        uq_pass = True
        for name, query in uq_queries:
            cursor.execute(query)
            dupes = cursor.fetchall()
            if dupes:
                uq_pass = False
                results["errors"].append(f"Uniqueness violation: found {len(dupes)} duplicate keys in {name}")
        results["checks"]["uniqueness"] = "PASS" if uq_pass else "FAIL"

        # Check C: NPI Luhn Validation
        cursor.execute("SELECT npi FROM providers")
        npis = [row["npi"] for row in cursor.fetchall()]
        invalid_npis = [npi for npi in npis if not validate_npi(npi)]
        if invalid_npis:
            results["checks"]["npi_validation"] = "FAIL"
            results["errors"].append(f"NPI validation failure: {len(invalid_npis)} invalid NPI checksums found.")
        else:
            results["checks"]["npi_validation"] = "PASS"

        # Check D: Financial Invariants
        # D1. Claim Header vs Claim Line Sum
        cursor.execute("""
            SELECT c.claim_id, c.total_billed_amount, COALESCE(SUM(cl.line_billed_amount), 0.00) AS line_sum
            FROM claims c
            LEFT JOIN claim_lines cl ON c.claim_id = cl.claim_id
            GROUP BY c.claim_id, c.total_billed_amount
            HAVING c.total_billed_amount != line_sum
        """)
        mismatched_claims = cursor.fetchall()

        # D2. Remittance Header vs Payment Sum
        cursor.execute("""
            SELECT r.remittance_id, r.total_paid_amount, COALESCE(SUM(p.paid_amount), 0.00) AS pmt_sum
            FROM remittances r
            LEFT JOIN payments p ON r.remittance_id = p.remittance_id
            GROUP BY r.remittance_id, r.total_paid_amount
            HAVING r.total_paid_amount != pmt_sum
        """)
        mismatched_remits = cursor.fetchall()

        # D3. Reconciliation Balance
        cursor.execute("""
            SELECT reconciliation_id, variance_amount, reconciliation_status
            FROM reconciliations
            WHERE reconciliation_status = 'BALANCED' AND variance_amount != 0.00
        """)
        unbalanced_recs = cursor.fetchall()

        # D4. Line units * unit_price == line_billed_amount
        cursor.execute("""
            SELECT claim_line_id
            FROM claim_lines
            WHERE line_billed_amount != ROUND(units * unit_price, 2)
        """)
        mismatched_lines = cursor.fetchall()

        fin_pass = (
            len(mismatched_claims) == 0 and
            len(mismatched_remits) == 0 and
            len(unbalanced_recs) == 0 and
            len(mismatched_lines) == 0
        )
        if not fin_pass:
            if mismatched_claims:
                results["errors"].append(f"{len(mismatched_claims)} claims have total_billed_amount != sum(claim_lines).")
            if mismatched_remits:
                results["errors"].append(f"{len(mismatched_remits)} remittances have total_paid_amount != sum(payments).")
            if unbalanced_recs:
                results["errors"].append(f"{len(unbalanced_recs)} reconciliations have non-zero variance.")
            if mismatched_lines:
                results["errors"].append(f"{len(mismatched_lines)} claim lines have line_billed_amount != units * unit_price.")
        results["checks"]["financial_invariants"] = "PASS" if fin_pass else "FAIL"

        # Check E: Temporal Chronology
        temporal_queries = [
            ("Claim Submission before Encounter DOS", "SELECT COUNT(*) AS cnt FROM claims c JOIN encounters e ON c.encounter_id = e.encounter_id WHERE c.submission_date < e.date_of_service"),
            ("Encounter Discharge before DOS", "SELECT COUNT(*) AS cnt FROM encounters WHERE discharge_date IS NOT NULL AND discharge_date < date_of_service"),
            ("Adjudication before Submission", "SELECT COUNT(*) AS cnt FROM claims WHERE adjudication_date IS NOT NULL AND adjudication_date < submission_date"),
            ("Payment before Adjudication", "SELECT COUNT(*) AS cnt FROM payments p JOIN claims c ON p.claim_id = c.claim_id WHERE c.adjudication_date IS NOT NULL AND p.payment_date < c.adjudication_date"),
        ]
        temp_pass = True
        for name, query in temporal_queries:
            cursor.execute(query)
            cnt = cursor.fetchone()["cnt"]
            if cnt > 0:
                temp_pass = False
                results["errors"].append(f"Temporal violation: {cnt} records with {name}.")
        results["checks"]["temporal_consistency"] = "PASS" if temp_pass else "FAIL"

        # Check F: Claim Lifecycle Rules
        cursor.execute("SELECT COUNT(*) AS cnt FROM claims WHERE current_status_code = 'Denied' AND is_reconciled = 0")
        unreconciled_denials = cursor.fetchone()["cnt"]

        cursor.execute("""
            SELECT COUNT(*) AS cnt
            FROM claims c
            LEFT JOIN payments p ON c.claim_id = p.claim_id
            WHERE c.current_status_code = 'Paid' AND (p.payment_id IS NULL AND c.total_billed_amount > 0.00)
        """)
        missing_paid_pmts = cursor.fetchone()["cnt"]

        lifecycle_pass = (unreconciled_denials == 0 and missing_paid_pmts == 0)
        if not lifecycle_pass:
            results["errors"].append("Claim lifecycle validation failed for Paid or Denied state consistency.")
        results["checks"]["claim_lifecycle"] = "PASS" if lifecycle_pass else "FAIL"

        # Check G: Clean Baseline Confirmation (No intentional errors)
        cursor.execute("SELECT COUNT(*) AS cnt FROM claims WHERE total_billed_amount < 0.00")
        neg_billed = cursor.fetchone()["cnt"]
        clean_baseline_pass = (neg_billed == 0 and len(results["errors"]) == 0)
        results["checks"]["clean_baseline"] = "PASS" if clean_baseline_pass else "FAIL"

        # 2. Compute Distributions
        cursor.execute("SELECT payer_type, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM payers) AS pct FROM payers GROUP BY payer_type")
        results["distributions"]["payer_types"] = {row["payer_type"]: float(row["pct"]) for row in cursor.fetchall()}

        cursor.execute("SELECT current_status_code, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS pct FROM claims GROUP BY current_status_code")
        results["distributions"]["claim_statuses"] = {row["current_status_code"]: float(row["pct"]) for row in cursor.fetchall()}

    if any(status == "FAIL" for status in results["checks"].values()):
        results["overall_status"] = "FAIL"

    return results

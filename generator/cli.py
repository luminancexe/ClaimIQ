"""Command-Line Interface and pipeline orchestrator for ClaimIQ Generator."""

import sys
import time
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List

from generator.config import GeneratorConfig, SCALE_PROFILES
from generator.random_state import GeneratorRandomState
from generator.database import (
    get_connection,
    safe_reset_database,
    bulk_insert,
    insert_and_fetch_mappings,
)
from generator.reference_data import verify_reference_data
from generator.validators import validate_database_dataset

# Entity Generators
from generator.generators.facilities import (
    generate_facilities,
    facilities_to_rows,
    FACILITIES_COLUMNS,
)
from generator.generators.payers import (
    generate_payers,
    payers_to_rows,
    PAYERS_COLUMNS,
)
from generator.generators.plans import (
    generate_insurance_plans,
    plans_to_rows,
    PLANS_COLUMNS,
)
from generator.generators.providers import (
    generate_providers,
    providers_to_rows,
    PROVIDERS_COLUMNS,
)
from generator.generators.patients import (
    generate_patients,
    patients_to_rows,
    PATIENTS_COLUMNS,
)
from generator.generators.coverage import (
    generate_patient_coverages,
    coverages_to_rows,
    COVERAGE_COLUMNS,
)
from generator.generators.encounters import (
    generate_encounters,
    encounters_to_rows,
    ENCOUNTERS_COLUMNS,
)
from generator.generators.diagnoses import (
    generate_encounter_diagnoses,
    diagnoses_to_rows,
    DIAGNOSES_COLUMNS,
)
from generator.generators.claims import (
    generate_claims_and_lines,
    claims_to_rows,
    CLAIMS_COLUMNS,
)
from generator.generators.claim_lines import (
    prepare_claim_line_rows,
    CLAIM_LINES_COLUMNS,
)
from generator.generators.claim_history import (
    generate_claim_status_history,
    CLAIM_STATUS_HISTORY_COLUMNS,
)
from generator.generators.remittances import (
    generate_remittances_and_payment_data,
    remittances_to_rows,
    REMITTANCES_COLUMNS,
)
from generator.generators.payments import (
    prepare_payment_rows,
    PAYMENTS_COLUMNS,
)
from generator.generators.adjustments import (
    prepare_adjustment_rows,
    ADJUSTMENTS_COLUMNS,
)
from generator.generators.denials import (
    prepare_denial_rows,
    DENIALS_COLUMNS,
)
from generator.generators.reconciliations import (
    prepare_reconciliation_rows,
    RECONCILIATIONS_COLUMNS,
)


def run_generation_pipeline(config: GeneratorConfig) -> Dict[str, Any]:
    """Execute the full deterministic generation pipeline."""
    start_time = time.time()
    rng = GeneratorRandomState(config.seed)
    profile = config.profile

    print("=" * 70)
    print("ClaimIQ Synthetic Healthcare Claims Generator — Phase 3")
    print(f"Scale: {profile.name.upper()} | Seed: {config.seed} | Batch Size: {config.batch_size}")
    print(f"Target DB: {config.db_user}@{config.db_host}:{config.db_port}/{config.db_name}")
    print("=" * 70)

    if config.dry_run:
        print("[DRY RUN] Simulating in-memory generation without database insertion...")
        # Simulate dry run
        facilities = generate_facilities(profile.num_facilities, rng)
        payers = generate_payers(profile.num_payers, rng)
        patients = generate_patients(profile.num_patients, rng)
        print(f"Plan: {len(facilities)} facilities, {len(payers)} payers, {len(patients)} patients.")
        print(f"Planned Target: {profile.num_claims} claims, {profile.num_encounters} encounters.")
        print("[DRY RUN] Simulation complete. Zero database modifications performed.")
        return {"status": "DRY_RUN_COMPLETE", "elapsed_seconds": time.time() - start_time}

    # Connect to MySQL
    conn = get_connection(config)
    try:
        # Step 1: Verify Static Reference Tables
        print("[1/17] Verifying static reference tables...")
        ref_status = verify_reference_data(conn)
        if not ref_status["is_valid"]:
            for err in ref_status["errors"]:
                print(f"  ERROR: {err}")
            raise RuntimeError("Static reference table verification failed.")

        # Step 2: Facilities
        print(f"[2/17] Generating {profile.num_facilities} facilities...")
        facilities = generate_facilities(profile.num_facilities, rng)
        fac_rows = facilities_to_rows(facilities)
        fac_id_map = insert_and_fetch_mappings(
            conn, "facilities", FACILITIES_COLUMNS, fac_rows, "facility_reference", "facility_id", config.batch_size
        )
        fac_ids = list(fac_id_map.values())

        # Step 3: Payers
        print(f"[3/17] Generating {profile.num_payers} payers...")
        payers = generate_payers(profile.num_payers, rng)
        payer_rows = payers_to_rows(payers)
        payer_id_map = insert_and_fetch_mappings(
            conn, "payers", PAYERS_COLUMNS, payer_rows, "payer_reference", "payer_id", config.batch_size
        )

        # Step 4: Insurance Plans
        print(f"[4/17] Generating {profile.num_plans} insurance plans...")
        plans = generate_insurance_plans(payers, payer_id_map, profile.num_plans, rng)
        plan_rows = plans_to_rows(plans)
        bulk_insert(conn, "insurance_plans", PLANS_COLUMNS, plan_rows, config.batch_size)

        # Fetch plan IDs & map to payer IDs
        with conn.cursor() as cur:
            cur.execute("SELECT plan_id, payer_id FROM insurance_plans")
            plan_db_records = cur.fetchall()
            plan_ids = [row["plan_id"] for row in plan_db_records]
            plan_to_payer_map = {row["plan_id"]: row["payer_id"] for row in plan_db_records}

        # Step 5: Providers
        print(f"[5/17] Generating {profile.num_providers} providers...")
        providers = generate_providers(profile.num_providers, fac_ids, rng)
        prov_rows = providers_to_rows(providers)
        prov_id_map = insert_and_fetch_mappings(
            conn, "providers", PROVIDERS_COLUMNS, prov_rows, "provider_reference", "provider_id", config.batch_size
        )

        # Step 6: Patients
        print(f"[6/17] Generating {profile.num_patients} patients...")
        patients = generate_patients(profile.num_patients, rng)
        pat_rows = patients_to_rows(patients)
        pat_id_map = insert_and_fetch_mappings(
            conn, "patients", PATIENTS_COLUMNS, pat_rows, "patient_reference", "patient_id", config.batch_size
        )

        # Step 7: Patient Coverage
        print(f"[7/17] Generating patient insurance coverage...")
        coverages = generate_patient_coverages(patients, pat_id_map, plan_ids, config.start_date, config.end_date, rng)
        cov_rows = coverages_to_rows(coverages)
        bulk_insert(conn, "patient_coverage", COVERAGE_COLUMNS, cov_rows, config.batch_size)

        # Step 8: Encounters
        print(f"[8/17] Generating {profile.num_encounters} clinical encounters...")
        encounters = generate_encounters(
            profile.num_encounters, coverages, providers, prov_id_map, fac_id_map, config.start_date, config.end_date, rng
        )
        enc_rows = encounters_to_rows(encounters)
        enc_id_map = insert_and_fetch_mappings(
            conn, "encounters", ENCOUNTERS_COLUMNS, enc_rows, "encounter_reference", "encounter_id", config.batch_size
        )

        # Step 9: Encounter Diagnoses
        print(f"[9/17] Generating encounter ICD-10 diagnoses...")
        diagnoses = generate_encounter_diagnoses(encounters, enc_id_map, rng)
        diag_rows = diagnoses_to_rows(diagnoses)
        bulk_insert(conn, "encounter_diagnoses", DIAGNOSES_COLUMNS, diag_rows, config.batch_size)

        # Step 10: Claims & Lines
        print(f"[10/17] Generating {profile.num_claims} claims and itemized lines...")
        claims, claim_lines = generate_claims_and_lines(
            profile.num_claims, encounters, enc_id_map, plans, plan_to_payer_map, payers, rng
        )
        claim_rows = claims_to_rows(claims)
        claim_id_map = insert_and_fetch_mappings(
            conn, "claims", CLAIMS_COLUMNS, claim_rows, "claim_reference", "claim_id", config.batch_size
        )

        # Step 11: Claim Lines Insertion
        print(f"[11/17] Inserting {len(claim_lines)} claim service lines...")
        cline_rows = prepare_claim_line_rows(claim_lines, claim_id_map)
        bulk_insert(conn, "claim_lines", CLAIM_LINES_COLUMNS, cline_rows, config.batch_size)

        # Step 12: Claim Status History
        print(f"[12/17] Generating claim lifecycle status history...")
        csh_rows = generate_claim_status_history(claims, claim_id_map)
        bulk_insert(conn, "claim_status_history", CLAIM_STATUS_HISTORY_COLUMNS, csh_rows, config.batch_size)

        # Step 13: Remittances
        print(f"[13/17] Generating electronic remittances...")
        remittances, payment_specs = generate_remittances_and_payment_data(claims, rng)
        remit_rows = remittances_to_rows(remittances)
        remit_id_map = insert_and_fetch_mappings(
            conn, "remittances", REMITTANCES_COLUMNS, remit_rows, "remittance_reference", "remittance_id", config.batch_size
        )

        # Step 14: Payments
        print(f"[14/17] Inserting {len(payment_specs)} payment allocations...")
        pmt_rows = prepare_payment_rows(payment_specs, remit_id_map, claim_id_map)
        bulk_insert(conn, "payments", PAYMENTS_COLUMNS, pmt_rows, config.batch_size)

        # Step 15: Adjustments
        print(f"[15/17] Inserting contractual and patient adjustments...")
        adj_rows = prepare_adjustment_rows(claims, claim_id_map)
        bulk_insert(conn, "adjustments", ADJUSTMENTS_COLUMNS, adj_rows, config.batch_size)

        # Step 16: Denials
        print(f"[16/17] Inserting formal denial determinations...")
        denial_rows = prepare_denial_rows(claims, claim_id_map)
        bulk_insert(conn, "denials", DENIALS_COLUMNS, denial_rows, config.batch_size)

        # Step 17: Reconciliations
        print(f"[17/17] Generating mathematical reconciliations...")
        rec_rows = prepare_reconciliation_rows(claims, claim_id_map)
        bulk_insert(conn, "reconciliations", RECONCILIATIONS_COLUMNS, rec_rows, config.batch_size)

        elapsed = time.time() - start_time
        print("-" * 70)
        print(f"Generation Complete! Elapsed Time: {elapsed:.2f} seconds.")
        print(f"Claims Generated: {len(claims):,} | Claim Lines: {len(claim_lines):,}")

        # Execute Auto-Validation
        print("\nExecuting comprehensive data quality validation...")
        val_results = validate_database_dataset(conn)
        print(f"Overall Validation Result: {val_results['overall_status']}")
        for check, res in val_results["checks"].items():
            print(f"  - {check.replace('_', ' ').title()}: {res}")

        if val_results["errors"]:
            print("\nValidation Errors Encountered:")
            for err in val_results["errors"]:
                print(f"  [!] {err}")

        return {
            "status": "SUCCESS",
            "elapsed_seconds": elapsed,
            "claims_count": len(claims),
            "lines_count": len(claim_lines),
            "validation": val_results,
        }

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="ClaimIQ Synthetic Healthcare Claims Data Generator")
    parser.add_argument("--scale", choices=["small", "medium", "large"], default="small", help="Dataset scale profile")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed (default: 42)")
    parser.add_argument("--batch-size", type=int, default=2500, help="Chunked batch insertion size (default: 2500)")
    parser.add_argument("--db-host", help="MySQL Host (default: 127.0.0.1 or env)")
    parser.add_argument("--db-port", type=int, help="MySQL Port (default: 3306 or env)")
    parser.add_argument("--db-name", help="MySQL Database name (default: claimiq_test or env)")
    parser.add_argument("--db-user", help="MySQL Username (default: root or env)")
    parser.add_argument("--db-password", help="MySQL Password")
    parser.add_argument("--dry-run", action="store_true", help="Simulate generation without writing to database")
    parser.add_argument("--validate", action="store_true", help="Run validation suite on existing database")
    parser.add_argument("--reset", action="store_true", help="Safely delete synthetic transactional data")

    args = parser.parse_args()

    config = GeneratorConfig(
        scale=args.scale,
        seed=args.seed,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        validate=args.validate,
        reset=args.reset,
    )
    if args.db_host:
        config.db_host = args.db_host
    if args.db_port:
        config.db_port = args.db_port
    if args.db_name:
        config.db_name = args.db_name
    if args.db_user:
        config.db_user = args.db_user
    if args.db_password is not None:
        config.db_password = args.db_password

    if config.reset:
        conn = get_connection(config)
        try:
            print("Executing safe database reset...")
            deleted = safe_reset_database(conn)
            print("Reset complete. Deleted record counts:")
            for tbl, cnt in deleted.items():
                print(f"  - {tbl}: {cnt:,} rows deleted")
        finally:
            conn.close()
        sys.exit(0)

    if config.validate:
        conn = get_connection(config)
        try:
            print("Running database validation suite...")
            res = validate_database_dataset(conn)
            print(f"Validation Status: {res['overall_status']}")
            for check, status in res["checks"].items():
                print(f"  - {check}: {status}")
            if res["errors"]:
                print("Errors:")
                for err in res["errors"]:
                    print(f"  [!] {err}")
        finally:
            conn.close()
        sys.exit(0)

    run_generation_pipeline(config)


if __name__ == "__main__":
    main()

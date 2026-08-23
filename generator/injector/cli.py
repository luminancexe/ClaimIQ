"""Command-Line Interface for ClaimIQ Anomaly Injection & Ground Truth Management."""

import sys
import argparse
from typing import List, Optional

from generator.config import GeneratorConfig
from generator.database import get_connection, safe_reset_database
from generator.injector.engine import AnomalyInjectionEngine
from generator.injector.ground_truth import (
    fetch_ground_truth_records,
    revert_ground_truth_mutations,
)
from generator.injector.validators import validate_injected_anomalies
from generator.injector.taxonomy import TAXONOMY, list_all_anomalies


def main():
    parser = argparse.ArgumentParser(description="ClaimIQ Phase 4 — Controlled Error Injection CLI")
    parser.add_argument("--profile", choices=["clean", "light", "moderate", "heavy", "targeted"], default="moderate", help="Anomaly injection profile")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed (default: 42)")
    parser.add_argument("--anomaly", help="Comma-separated anomaly codes (e.g. E001,E023) or category for targeted injection")
    parser.add_argument("--count", type=int, help="Override number of mutations per anomaly code")
    parser.add_argument("--rate", type=float, help="Target mutation rate percentage (0.01 to 1.0)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate planned mutations without modifying database")
    parser.add_argument("--validate", action="store_true", help="Audit database to verify injected mutations against ground truth")
    parser.add_argument("--report", action="store_true", help="Display summary of active ground truth anomalies")
    parser.add_argument("--reset-anomalies", action="store_true", help="Revert all active injected anomalies to restore clean baseline")
    parser.add_argument("--reset", action="store_true", help="Fully purge all synthetic transactions, anomalies, and ground truth")
    parser.add_argument("--list-taxonomy", action="store_true", help="List all 67 registered anomaly definitions and exit")

    # Database connection overrides
    parser.add_argument("--db-host", help="MySQL Host")
    parser.add_argument("--db-port", type=int, help="MySQL Port")
    parser.add_argument("--db-name", help="MySQL Database name")
    parser.add_argument("--db-user", help="MySQL Username")
    parser.add_argument("--db-password", help="MySQL Password")

    args = parser.parse_args()

    if args.list_taxonomy:
        print("=" * 80)
        print("ClaimIQ Phase 4 Anomaly Taxonomy Registry (67 Definitions)")
        print("=" * 80)
        for defn in list_all_anomalies():
            print(f"[{defn.code}] {defn.name.ljust(45)} | Severity: {defn.severity.value.ljust(8)} | Category: {defn.category.value}")
        sys.exit(0)

    config = GeneratorConfig(
        seed=args.seed,
        dry_run=args.dry_run,
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

    if args.reset:
        conn = get_connection(config)
        try:
            print("Executing full database reset...")
            deleted = safe_reset_database(conn)
            print("Full reset complete:")
            for tbl, cnt in deleted.items():
                print(f"  - {tbl}: {cnt:,} rows deleted")
        finally:
            conn.close()
        sys.exit(0)

    if args.reset_anomalies:
        conn = get_connection(config)
        try:
            print("Reverting all active injected anomalies to restore clean baseline...")
            res = revert_ground_truth_mutations(conn)
            print(f"Reversion complete:")
            print(f"  - Restored column values: {res['reverted_count']}")
            print(f"  - Deleted duplicate/clone records: {res['deleted_inserted_records']}")
            print(f"  - Total ground truth records deactivated: {res['total_records_processed']}")
        finally:
            conn.close()
        sys.exit(0)

    if args.validate:
        conn = get_connection(config)
        try:
            print("Auditing database for active anomaly mutations against ground truth...")
            val = validate_injected_anomalies(conn)
            print(f"Overall Status: {val['overall_status']}")
            print(f"Active Ground Truth Records: {val['active_ground_truth_count']}")
            print(f"Verified Live Mutations: {val['verified_mutations']}")
            print(f"Mismatched / Missing Mutations: {val['mismatched_mutations']}")
            if val["category_counts"]:
                print("\nCategory Distribution:")
                for cat, cnt in val["category_counts"].items():
                    print(f"  - {cat}: {cnt}")
            if val["errors"]:
                print("\nValidation Errors:")
                for err in val["errors"]:
                    print(f"  [!] {err}")
        finally:
            conn.close()
        sys.exit(0)

    if args.report:
        conn = get_connection(config)
        try:
            records = fetch_ground_truth_records(conn, active_only=True)
            print("=" * 80)
            print(f"ClaimIQ Active Ground Truth Report ({len(records)} Active Anomalies)")
            print("=" * 80)
            for r in records[:20]:
                print(f"[{r.anomaly_code}] {r.target_table}.{r.target_column} (ID: {r.target_record_id}) | Original: {r.original_value} -> Mutated: {r.mutated_value}")
            if len(records) > 20:
                print(f"... and {len(records) - 20} more records.")
        finally:
            conn.close()
        sys.exit(0)

    # Parse targeted anomaly codes if specified
    target_codes: Optional[List[str]] = None
    if args.anomaly:
        raw_codes = [c.strip().upper() for c in args.anomaly.split(",")]
        target_codes = [c for c in raw_codes if c in TAXONOMY]
        profile_name = "targeted"
    else:
        profile_name = args.profile

    print("=" * 80)
    print("ClaimIQ Phase 4 — Controlled Error Injection Engine")
    print(f"Profile: {profile_name.upper()} | Seed: {config.seed} | Mode: {'DRY RUN' if config.dry_run else 'DATABASE MUTATION'}")
    print(f"Target DB: {config.db_user}@{config.db_host}:{config.db_port}/{config.db_name}")
    print("=" * 80)

    engine = AnomalyInjectionEngine(config, profile_name=profile_name, seed=config.seed)
    result = engine.execute_injection(target_codes=target_codes, override_count=args.count)

    print("\nInjection Execution Summary:")
    print(f"  - Status: {result['status']}")
    print(f"  - Anomalies Injected: {result['anomalies_injected']:,}")
    print(f"  - Distinct Anomaly Types: {result.get('distinct_anomaly_types', 0)}")
    print(f"  - Elapsed Time: {result['elapsed_seconds']:.2f}s")
    if result.get("ground_truth_json"):
        print(f"  - Ground Truth Export: {result['ground_truth_json']}")

    if result.get("category_breakdown"):
        print("\nBreakdown by Category:")
        for cat, cnt in result["category_breakdown"].items():
            print(f"  - {cat.ljust(35)}: {cnt} anomalies")

    if result.get("severity_breakdown"):
        print("\nBreakdown by Severity:")
        for sev, cnt in result["severity_breakdown"].items():
            print(f"  - {sev.ljust(15)}: {cnt} anomalies")

    if not config.dry_run and result["anomalies_injected"] > 0:
        print("\nRunning automated Phase 4 validation...")
        conn = get_connection(config)
        try:
            val_res = validate_injected_anomalies(conn)
            print(f"Validation Result: {val_res['overall_status']} ({val_res['verified_mutations']} / {val_res['active_ground_truth_count']} mutations verified)")
        finally:
            conn.close()


if __name__ == "__main__":
    main()

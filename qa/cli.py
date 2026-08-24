"""Command-Line Interface for ClaimIQ Phase 5 QA Rule Engine."""

import sys
import argparse
from typing import List, Optional

from generator.database import get_connection
from generator.config import GeneratorConfig
from qa.config import QAConfig
from qa.registry import list_all_rules, QA_RULE_REGISTRY
from qa.engine import QAExecutionEngine
from qa.validators import validate_clean_baseline_qa, audit_rule_registry_integrity


def main():
    parser = argparse.ArgumentParser(description="ClaimIQ Phase 5 — Data Quality & QA Rule Engine CLI")
    parser.add_argument("--run", action="store_true", help="Execute QA rule engine against the database")
    parser.add_argument("--rule", help="Comma-separated rule codes (e.g. R-E023,R-E030 or E023,E030)")
    parser.add_argument("--category", help="Filter by QA category (COMPLETENESS, VALIDITY, UNIQUENESS, FINANCIAL, TEMPORAL, REFERENTIAL, BUSINESS_LOGIC)")
    parser.add_argument("--dimension", help="Filter by DQ dimension (Referential Integrity, Financial, Completeness, Validity, Uniqueness, Temporal, Accuracy)")
    parser.add_argument("--batch-id", help="Custom batch identifier (default: BATCH-YYYYMMDD-HHMMSS)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without persisting results or issues to MySQL")
    parser.add_argument("--validate-ground-truth", action="store_true", help="Evaluate detection findings against Phase 4 anomaly ground truth")
    parser.add_argument("--validate-clean", action="store_true", help="Execute audit verifying zero unexpected defects on clean baseline")
    parser.add_argument("--report", action="store_true", help="Display detailed Data Quality Score and detection findings report")
    parser.add_argument("--list-rules", action="store_true", help="List all 67 registered QA rules and exit")

    # Database connection overrides
    parser.add_argument("--db-host", help="MySQL Host")
    parser.add_argument("--db-port", type=int, help="MySQL Port")
    parser.add_argument("--db-name", help="MySQL Database name")
    parser.add_argument("--db-user", help="MySQL Username")
    parser.add_argument("--db-password", help="MySQL Password")

    args = parser.parse_args()

    if args.list_rules:
        print("=" * 90)
        print("ClaimIQ Phase 5 QA Rule Registry (67 Rules)")
        print("=" * 90)
        for r in list_all_rules():
            anoms = ",".join(r.anomaly_codes)
            print(f"[{r.rule_code.ljust(8)}] {r.rule_name.ljust(48)} | Dim: {r.dimension_code.ljust(20)} | Sev: {r.default_severity_code.ljust(8)} | Anom: {anoms}")
        sys.exit(0)

    config = QAConfig(
        dry_run=args.dry_run,
        validate_ground_truth=args.validate_ground_truth,
    )
    if args.batch_id:
        config.batch_identifier = args.batch_id
    if args.rule:
        config.rule_filter = [r.strip() for r in args.rule.split(",")]
    if args.category:
        config.category_filter = args.category.strip()
    if args.dimension:
        config.dimension_filter = args.dimension.strip()

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

    if args.validate_clean:
        gen_cfg = GeneratorConfig(
            db_host=config.db_host,
            db_port=config.db_port,
            db_name=config.db_name,
            db_user=config.db_user,
            db_password=config.db_password,
        )
        conn = get_connection(gen_cfg)
        try:
            print("Auditing clean baseline integrity with all 67 QA rules...")
            res = validate_clean_baseline_qa(conn)
            print(f"Clean Baseline Status: {res['status']}")
            print(f"Rules Evaluated: {res['rules_evaluated']}")
            print(f"Total Records Scanned: {res['total_records_scanned']:,}")
            print(f"Unexpected Findings Count: {res['unexpected_finding_count']}")
            if res["findings"]:
                print("\nUnexpected Findings Preview:")
                for f in res["findings"]:
                    print(f"  [!] {f['rule_code']} ({f['anomaly_code']}): {f['explanation']}")
        finally:
            conn.close()
        sys.exit(0)

    print("=" * 90)
    print("ClaimIQ Phase 5 — Data Quality & QA Rule Engine")
    print(f"Batch ID: {config.batch_identifier} | Mode: {'DRY RUN' if config.dry_run else 'DATABASE EXECUTION'}")
    print(f"Target DB: {config.db_user}@{config.db_host}:{config.db_port}/{config.db_name}")
    print("=" * 90)

    engine = QAExecutionEngine(config)
    result = engine.execute()

    print("\nExecution Run Summary:")
    print(f"  - Run Reference: {result['run_reference']}")
    print(f"  - Status: {result['status']}")
    print(f"  - Rules Evaluated: {result['rules_evaluated']}")
    print(f"  - Total Records Scanned: {result['total_records_evaluated']:,}")
    print(f"  - Total Defects Detected: {result['total_issues_detected']:,}")
    print(f"  - Overall DQ Score: {result['overall_dq_score']:.2f} / 100.00")
    print(f"  - Execution Latency: {result['execution_duration_seconds']:.2f}s")

    dq_sum = result.get("dq_summary", {})
    if dq_sum.get("dimension_scores"):
        print("\nData Quality Dimension Breakdown:")
        print(f"  {'Dimension':<25} | {'Weight':<6} | {'Scanned':<10} | {'Defects':<8} | {'Raw Score':<10} | {'Weighted Score'}")
        print("  " + "-" * 78)
        for dim, s in dq_sum["dimension_scores"].items():
            scanned_str = f"{s['records_evaluated']:,}".ljust(10)
            defects_str = f"{s['issues_detected']:,}".ljust(8)
            print(f"  {dim:<25} | {s['weight']:<6.2f} | {scanned_str} | {defects_str} | {s['raw_score']:<10.2f} | {s['weighted_score']:.2f}")

    if result.get("ground_truth_evaluation"):
        gt = result["ground_truth_evaluation"]
        print("\nGround Truth Evaluation Metrics:")
        print(f"  - Active Ground Truth Anomalies : {gt['total_ground_truth_anomalies']}")
        print(f"  - Live QA Detections            : {gt['total_qa_detections']}")
        print(f"  - True Positives (TP)           : {gt['true_positives']}")
        print(f"  - False Positives (FP)          : {gt['false_positives']}")
        print(f"  - False Negatives (FN)          : {gt['false_negatives']}")
        print(f"  - Precision                     : {gt['precision'] * 100:.2f}%")
        print(f"  - Recall (Detection Rate)       : {gt['recall'] * 100:.2f}%")
        print(f"  - F1 Score                      : {gt['f1_score']:.4f}")

    if args.report and result.get("detections"):
        print("\nDetected Findings Preview (first 15):")
        for d in result["detections"][:15]:
            print(f"  [{d['rule_code']}] ({d['anomaly_code']}) {d['target_table']}.{d['target_column']} ID:{d['target_record_id']} | Sev: {d['severity_code']} | {d['explanation']}")


if __name__ == "__main__":
    main()

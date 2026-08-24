"""Command-Line Interface for ClaimIQ Phase 6 Analytics Engine."""

import sys
import json
import argparse
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from analytics.config import AnalyticsConfig
from analytics.engine import AnalyticsExecutionEngine


def parse_date(date_str: str) -> Optional[date]:
    """Parse YYYY-MM-DD string into a datetime.date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD.") from e


def main():
    parser = argparse.ArgumentParser(
        description="ClaimIQ Phase 6 — Python Analytics Engine & Advanced Data Quality Analytics CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--report",
        choices=["overview", "financial", "kpis", "provider", "payer", "trends", "root-cause", "recurrence", "all"],
        default="overview",
        help="Select analytics report type to generate (default: overview)",
    )
    parser.add_argument("--batch-id", help="Filter analytics by batch identifier")
    parser.add_argument("--start-date", type=parse_date, help="Filter records from date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=parse_date, help="Filter records to date (YYYY-MM-DD)")
    parser.add_argument("--provider", help="Filter by provider reference or ID (e.g. PRV-2026-0000001)")
    parser.add_argument("--payer", help="Filter by payer reference or ID (e.g. PAY-2026-0000001)")
    parser.add_argument("--trend-interval", choices=["daily", "weekly", "monthly"], default="monthly", help="Time bucket interval for DQ trends")
    parser.add_argument("--dry-run", action="store_true", help="Simulate analytics without requiring live MySQL connection")
    parser.add_argument("--output", help="Optional path to export full JSON report")

    # Database connection parameters
    parser.add_argument("--db-host", help="MySQL Host")
    parser.add_argument("--db-port", type=int, help="MySQL Port")
    parser.add_argument("--db-name", help="MySQL Database name")
    parser.add_argument("--db-user", help="MySQL Username")
    parser.add_argument("--db-password", help="MySQL Password")

    args = parser.parse_args()

    config = AnalyticsConfig(
        report_type=args.report,
        batch_identifier=args.batch_id,
        start_date=args.start_date,
        end_date=args.end_date,
        provider_filter=args.provider,
        payer_filter=args.payer,
        trend_interval=args.trend_interval,
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

    print("=" * 90)
    print("ClaimIQ Phase 6 — Python Analytics Engine")
    print(f"Report: {config.report_type.upper()} | Mode: {'DRY RUN' if config.dry_run else 'DATABASE EXECUTION'}")
    print(f"Target DB: {config.db_user}@{config.db_host}:{config.db_port}/{config.db_name}")
    print("=" * 90)

    engine = AnalyticsExecutionEngine(config)
    report = engine.execute()

    print(f"\nExecution Report ID: {report.report_id} (Duration: {report.telemetry.execution_duration_ms if report.telemetry else 0}ms)")

    # 1. Financial Report Output
    if report.financial:
        f = report.financial
        print("\n" + "-" * 90)
        print("1. FINANCIAL EXPOSURE & RECONCILIATION SUMMARY")
        print("-" * 90)
        print(f"  Total Billed Amount            : ${float(f.total_billed):>14,.2f}")
        print(f"  Total Paid Amount              : ${float(f.total_paid):>14,.2f}")
        print(f"  Total Contractual Adjustments  : ${float(f.total_contractual_adjustments):>14,.2f}")
        print(f"  Total Patient Responsibility   : ${float(f.total_patient_responsibility):>14,.2f}")
        print(f"  Total Reconciliation Variance  : ${float(f.total_variance):>14,.2f}")
        print(f"  Unreconciled Billed Amount     : ${float(f.unreconciled_amount):>14,.2f}")
        print(f"  Overpayment Exposure at Risk   : ${float(f.overpayment_exposure):>14,.2f}")
        print(f"  Underpayment Exposure at Risk  : ${float(f.underpayment_exposure):>14,.2f}")
        print(f"  Total Denied Billed Exposure   : ${float(f.total_denied_amount):>14,.2f}")
        print(f"  Payment Conversion Rate        : {f.payment_rate:>13.2f}%")
        print(f"  Reconciliation Rate (Eligible) : {f.reconciliation_rate:>13.2f}%")
        print(f"  Financial Integrity Rate       : {f.financial_integrity_rate:>13.2f}%")

    # 2. KPIs Output
    if report.kpis:
        k = report.kpis
        print("\n" + "-" * 90)
        print("2. OPERATIONAL & QUALITY ASSURANCE KPIS")
        print("-" * 90)
        print(f"  Claims Volume & Status Breakdown (Total: {k.claims.total_claims:,}):")
        for st, cnt in k.claims.status_distribution.items():
            print(f"    - {st:<20}: {cnt:>6,} claims ({(cnt / max(k.claims.total_claims, 1) * 100):>5.1f}%)")
        print(f"  Adjudication Rate              : {k.claims.adjudication_rate:.2f}% ({k.claims.adjudicated_claims:,} adjudicated)")
        print(f"  Reconciled Finalized Claims    : {k.claims.reconciled_claims:,}")
        print(f"  Average Payment Disbursement   : ${float(k.payments.average_payment_amount):,.2f} ({k.payments.total_payments_count:,} disbursements)")
        if k.payments.average_payment_turnaround_days is not None:
            print(f"  Average Payment Turnaround     : {k.payments.average_payment_turnaround_days:.1f} days")
        print(f"  Denial Rate (Adjudicated)      : {k.denials.denial_rate:.2f}% ({k.denials.total_denials:,} denials)")
        print(f"  Appealable Denial Ratio        : {k.denials.appealable_rate:.2f}%")
        print(f"  Total QA Issues Detected       : {k.qa.total_issues:,} (Defect Density: {k.qa.defect_density:.4f})")
        print(f"  Clean Record Rate              : {k.qa.clean_record_rate:.2f}%")
        print(f"  Average QA Data Quality Score  : {k.qa.average_dq_score:.2f} / 100.00")

    # 3. Provider Scorecards Output
    if report.provider_scorecards:
        print("\n" + "-" * 90)
        print(f"3. PROVIDER QUALITY SCORECARDS (Showing {len(report.provider_scorecards)} Providers)")
        print("-" * 90)
        print(f"  {'Provider':<24} | {'Specialty':<18} | {'Claims':<6} | {'Billed':<10} | {'Paid':<10} | {'Denial%':<7} | {'DQ Score':<8}")
        print("  " + "-" * 88)
        for p in report.provider_scorecards[:10]:
            p_name = p.provider_name[:24]
            p_spec = p.specialty[:18]
            print(f"  {p_name:<24} | {p_spec:<18} | {p.claim_volume:<6} | ${float(p.total_billed):<9,.2f} | ${float(p.total_paid):<9,.2f} | {p.denial_rate:<6.1f}% | {p.dq_score:>6.1f}")

    # 4. Payer Scorecards Output
    if report.payer_scorecards:
        print("\n" + "-" * 90)
        print(f"4. PAYER ADJUDICATION SCORECARDS (Showing {len(report.payer_scorecards)} Payers)")
        print("-" * 90)
        print(f"  {'Payer':<24} | {'Type':<12} | {'Claims':<6} | {'Billed':<10} | {'Denial%':<7} | {'Pmt Rate%':<9} | {'Adj Lat':<7} | {'Pmt Lat'}")
        print("  " + "-" * 88)
        for py in report.payer_scorecards[:10]:
            py_name = py.payer_name[:24]
            print(f"  {py_name:<24} | {py.payer_type:<12} | {py.claim_volume:<6} | ${float(py.total_billed):<9,.2f} | {py.denial_rate:<6.1f}% | {py.payment_rate:>8.1f}% | {py.average_adjudication_latency_days:>5.1f}d | {py.average_payment_latency_days:>5.1f}d")

    # 5. DQ Trends Output
    if report.dq_trends:
        t = report.dq_trends
        print("\n" + "-" * 90)
        print(f"5. LONGITUDINAL DATA QUALITY TRENDS ({t.interval.upper()} Series - Trajectory: {t.trend_direction})")
        print("-" * 90)
        print(f"  {'Bucket':<12} | {'Claims':<8} | {'Issues':<8} | {'Overall DQ Score':<16} | {'Score Velocity'}")
        print("  " + "-" * 60)
        for pt in t.points:
            print(f"  {pt.time_bucket:<12} | {pt.claim_volume:<8,} | {pt.issue_count:<8,} | {pt.overall_dq_score:>14.2f}  | {t.score_velocity:>+10.2f}")
        print(f"  Rolling Mean DQ Score: {t.rolling_average_score:.2f} / 100.00")

    # 6. Root Cause / Pareto Output
    if report.root_cause:
        rc = report.root_cause
        print("\n" + "-" * 90)
        print(f"6. ROOT CAUSE & PARETO DEFECT DISTRIBUTION (Analyzed {rc.total_issues_analyzed:,} Issues)")
        print("-" * 90)
        print(f"  Primary Defect Driver: {rc.primary_defect_driver}")
        print(f"  {'Anomaly':<8} | {'Category':<15} | {'Severity':<8} | {'Issues':<6} | {'% Total':<8} | {'Cum %':<8} | {'Financial Exposure'}")
        print("  " + "-" * 88)
        for idx, item in enumerate(rc.items[:10]):
            pareto_mark = " [*]" if idx <= rc.pareto_cutoff_index else ""
            print(f"  {item.anomaly_code:<8} | {item.anomaly_category:<15} | {item.severity_code:<8} | {item.issue_count:<6} | {item.percentage_of_total:>6.1f}% | {item.cumulative_percentage:>6.1f}%{pareto_mark:<3} | ${float(item.financial_exposure):,.2f}")
        print("  [*] Indicates vital few anomaly drivers within 80% Pareto cutoff threshold.")

    # 7. Recurrence Patterns Output
    if report.recurrence:
        rec = report.recurrence
        print("\n" + "-" * 90)
        print(f"7. RECURRING DEFECT PATTERNS ({rec.recurring_cluster_count} Clusters - Repeat Rate: {rec.repeat_issue_rate:.2f}%)")
        print("-" * 90)
        if rec.top_repeat_entities:
            print(f"  {'Rank':<4} | {'Entity Type':<12} | {'Entity Reference':<24} | {'Anomaly':<8} | {'Repeats'}")
            print("  " + "-" * 60)
            for p in rec.top_repeat_entities[:10]:
                print(f"  #{p.recurrence_rank:<3} | {p.entity_type:<12} | {p.entity_identifier:<24} | {p.anomaly_code:<8} | {p.occurrence_count:>4} occurrences")
        else:
            print("  Zero recurring defect clusters identified (Clean baseline state).")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\nFull analytical report exported to: {args.output}")


if __name__ == "__main__":
    main()

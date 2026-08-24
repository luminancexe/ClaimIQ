"""Pareto 80/20 root cause analysis and defect concentration distributions."""

from decimal import Decimal
from typing import Optional, List, Dict, Any
import pymysql
from analytics.config import AnalyticsConfig
from analytics.models import RootCauseItem, RootCauseDistribution
from analytics.database import execute_analytical_query
from generator.financials import quantize_currency
from qa.registry import get_rule


def calculate_root_cause_distribution(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> RootCauseDistribution:
    """Analyze defect distributions using Pareto 80/20 analysis, ranking concentration drivers."""
    if conn is None:
        # Standalone simulated dry-run default
        items = [
            RootCauseItem(
                anomaly_category="Financial",
                anomaly_code="E023",
                rule_code="R-E023",
                description="Payment Exceeds Total Billed Amount (Overpayment)",
                severity_code="Critical",
                dimension_code="Financial",
                issue_count=15,
                percentage_of_total=50.00,
                cumulative_percentage=50.00,
                financial_exposure=Decimal("12500.00"),
            ),
            RootCauseItem(
                anomaly_category="Temporal",
                anomaly_code="E034",
                rule_code="R-E034",
                description="Clinical DOS Precedes Claim Submission",
                severity_code="High",
                dimension_code="Temporal",
                issue_count=10,
                percentage_of_total=33.33,
                cumulative_percentage=83.33,
                financial_exposure=Decimal("0.00"),
            ),
            RootCauseItem(
                anomaly_category="Completeness",
                anomaly_code="E001",
                rule_code="R-E001",
                description="Mandatory Patient State Completeness",
                severity_code="Low",
                dimension_code="Completeness",
                issue_count=5,
                percentage_of_total=16.67,
                cumulative_percentage=100.00,
                financial_exposure=Decimal("0.00"),
            ),
        ]
        return RootCauseDistribution(
            items=items,
            pareto_cutoff_index=1,  # first 2 items reach 83.33% >= 80%
            primary_defect_driver="Financial / Overpayment (E023)",
            total_issues_analyzed=30,
        )

    sql = """
        SELECT 
            r.rule_code,
            r.rule_name,
            r.dimension_code,
            r.default_severity_code AS severity_code,
            cat.category_name,
            COUNT(i.issue_id) AS issue_cnt,
            COALESCE(SUM(i.variance_amount), 0.00) AS financial_exposure
        FROM issues i
        JOIN qa_rules r ON i.rule_id = r.rule_id
        LEFT JOIN qa_rule_categories cat ON r.category_id = cat.category_id
        GROUP BY r.rule_code, r.rule_name, r.dimension_code, r.default_severity_code, cat.category_name
        ORDER BY issue_cnt DESC, financial_exposure DESC, r.rule_code ASC
    """
    rows = execute_analytical_query(conn, sql)
    total_issues = sum(r["issue_cnt"] for r in rows)

    if total_issues == 0:
        return RootCauseDistribution(
            items=[],
            pareto_cutoff_index=0,
            primary_defect_driver="None (Clean Dataset - Zero Defect Findings)",
            total_issues_analyzed=0,
        )

    items: List[RootCauseItem] = []
    cumulative_pct = 0.0
    pareto_cutoff_index = 0
    cutoff_found = False

    for idx, r in enumerate(rows):
        cnt = r["issue_cnt"]
        pct = (float(cnt) / float(total_issues)) * 100.0
        cumulative_pct += pct
        if cumulative_pct > 100.0:
            cumulative_pct = 100.0

        if cumulative_pct >= 80.0 and not cutoff_found:
            pareto_cutoff_index = idx
            cutoff_found = True

        anom_code = "UNKNOWN"
        try:
            rule_def = get_rule(r["rule_code"])
            if rule_def.anomaly_codes:
                anom_code = rule_def.anomaly_codes[0]
        except Exception:
            pass

        items.append(
            RootCauseItem(
                anomaly_category=r["category_name"] or r["dimension_code"],
                anomaly_code=anom_code,
                rule_code=r["rule_code"],
                description=r["rule_name"],
                severity_code=r["severity_code"],
                dimension_code=r["dimension_code"],
                issue_count=cnt,
                percentage_of_total=pct,
                cumulative_percentage=cumulative_pct,
                financial_exposure=quantize_currency(r["financial_exposure"]),
            )
        )

    primary_driver = f"{items[0].anomaly_category} ({items[0].anomaly_code}: {items[0].description})" if items else "None"

    return RootCauseDistribution(
        items=items,
        pareto_cutoff_index=pareto_cutoff_index,
        primary_defect_driver=primary_driver,
        total_issues_analyzed=total_issues,
    )

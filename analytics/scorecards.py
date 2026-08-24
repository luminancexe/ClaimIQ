"""Provider Quality Scorecards and Payer Adjudication Scorecards."""

from decimal import Decimal
from typing import Optional, List, Dict, Any
import pymysql
from analytics.config import AnalyticsConfig
from analytics.models import ProviderScorecard, PayerScorecard
from analytics.database import execute_analytical_query
from generator.financials import quantize_currency


def generate_provider_scorecards(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> List[ProviderScorecard]:
    """Generate deterministic quality, volume, and financial performance scorecards per healthcare provider."""
    if conn is None:
        return [
            ProviderScorecard(
                provider_id=1,
                provider_reference="PRV-2026-0000001",
                provider_name="Dr. Sarah Smith, MD",
                specialty="Internal Medicine",
                facility_id=1,
                facility_name="General Medical Center",
                claim_volume=150,
                total_billed=Decimal("37500.00"),
                total_paid=Decimal("30000.00"),
                payment_rate=80.00,
                denial_rate=5.00,
                issue_count=0,
                issue_density=0.0000,
                dq_score=100.00,
                financial_exposure=Decimal("0.00"),
            )
        ]

    filter_sql = ""
    params = []
    if config and config.provider_filter:
        filter_sql = "WHERE p.provider_reference = %s OR p.provider_id = %s"
        params.extend([config.provider_filter, config.provider_filter])

    # Safe aggregation using CTEs / subqueries to prevent one-to-many Cartesian products
    sql = f"""
        SELECT 
            p.provider_id,
            p.provider_reference,
            CONCAT(p.first_name, ' ', p.last_name) AS provider_name,
            p.specialty,
            p.facility_id,
            f.facility_name,
            COUNT(c.claim_id) AS claim_volume,
            COALESCE(SUM(c.total_billed_amount), 0.00) AS total_billed,
            COALESCE(pmt.total_paid, 0.00) AS total_paid,
            COUNT(CASE WHEN c.current_status_code = 'Denied' THEN 1 END) AS denied_count,
            COALESCE(iss.issue_count, 0) AS issue_count,
            COALESCE(iss.financial_exposure, 0.00) AS financial_exposure
        FROM providers p
        LEFT JOIN facilities f ON p.facility_id = f.facility_id
        LEFT JOIN claims c ON p.provider_id = c.billing_provider_id
        LEFT JOIN (
            SELECT c2.billing_provider_id, SUM(pm.paid_amount) AS total_paid
            FROM payments pm
            JOIN claims c2 ON pm.claim_id = c2.claim_id
            GROUP BY c2.billing_provider_id
        ) pmt ON p.provider_id = pmt.billing_provider_id
        LEFT JOIN (
            SELECT c3.billing_provider_id, COUNT(i.issue_id) AS issue_count, SUM(COALESCE(i.variance_amount, 0.00)) AS financial_exposure
            FROM issues i
            JOIN claims c3 ON i.claim_id = c3.claim_id
            GROUP BY c3.billing_provider_id
        ) iss ON p.provider_id = iss.billing_provider_id
        {filter_sql}
        GROUP BY p.provider_id, p.provider_reference, p.first_name, p.last_name, p.specialty, p.facility_id, f.facility_name, pmt.total_paid, iss.issue_count, iss.financial_exposure
        HAVING claim_volume > 0
        ORDER BY claim_volume DESC, total_billed DESC, p.provider_id ASC
    """

    rows = execute_analytical_query(conn, sql, tuple(params) if params else None)
    scorecards: List[ProviderScorecard] = []

    for r in rows:
        vol = r["claim_volume"]
        billed = quantize_currency(r["total_billed"])
        paid = quantize_currency(r["total_paid"])
        denied_cnt = r["denied_count"]
        iss_cnt = r["issue_count"]
        fin_exp = quantize_currency(r["financial_exposure"])

        pmt_rate = (float(paid) / float(billed) * 100.0) if billed > Decimal("0.00") else 100.0
        den_rate = (float(denied_cnt) / float(vol) * 100.0) if vol > 0 else 0.0
        density = (float(iss_cnt) / float(vol)) if vol > 0 else 0.0
        dq_score = max(0.0, 100.0 - (density * 100.0 * 2.0))

        scorecards.append(
            ProviderScorecard(
                provider_id=r["provider_id"],
                provider_reference=r["provider_reference"],
                provider_name=r["provider_name"],
                specialty=r["specialty"],
                facility_id=r["facility_id"],
                facility_name=r["facility_name"],
                claim_volume=vol,
                total_billed=billed,
                total_paid=paid,
                payment_rate=pmt_rate,
                denial_rate=den_rate,
                issue_count=iss_cnt,
                issue_density=density,
                dq_score=dq_score,
                financial_exposure=fin_exp,
            )
        )

    return scorecards


def generate_payer_scorecards(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> List[PayerScorecard]:
    """Generate adjudication efficiency, turnaround latency, and denial scorecards per payer."""
    if conn is None:
        return [
            PayerScorecard(
                payer_id=1,
                payer_reference="PAY-2026-0000001",
                payer_name="Blue Cross Commercial",
                payer_type="Commercial",
                claim_volume=300,
                total_billed=Decimal("75000.00"),
                total_paid=Decimal("60000.00"),
                denial_rate=8.00,
                payment_rate=80.00,
                average_adjudication_latency_days=5.20,
                average_payment_latency_days=7.40,
                timely_filing_compliance_rate=100.00,
                contractual_adjustment_ratio=15.00,
                issue_count=0,
            )
        ]

    filter_sql = ""
    params = []
    if config and config.payer_filter:
        filter_sql = "WHERE py.payer_reference = %s OR py.payer_id = %s"
        params.extend([config.payer_filter, config.payer_filter])

    sql = f"""
        SELECT 
            py.payer_id,
            py.payer_reference,
            py.payer_name,
            py.payer_type,
            py.timely_filing_days,
            COUNT(c.claim_id) AS claim_volume,
            COALESCE(SUM(c.total_billed_amount), 0.00) AS total_billed,
            COALESCE(pmt.total_paid, 0.00) AS total_paid,
            COUNT(CASE WHEN c.current_status_code = 'Denied' THEN 1 END) AS denied_count,
            AVG(CASE WHEN c.adjudication_date IS NOT NULL AND c.adjudication_date >= c.submission_date 
                     THEN DATEDIFF(c.adjudication_date, c.submission_date) END) AS avg_adj_latency,
            COALESCE(pmt.avg_pmt_latency, 0.00) AS avg_pmt_latency,
            COUNT(CASE WHEN DATEDIFF(c.submission_date, e.date_of_service) <= py.timely_filing_days THEN 1 END) AS timely_count,
            COALESCE(adj.total_co, 0.00) AS total_co,
            COALESCE(iss.issue_count, 0) AS issue_count
        FROM payers py
        LEFT JOIN claims c ON py.payer_id = c.payer_id
        LEFT JOIN encounters e ON c.encounter_id = e.encounter_id
        LEFT JOIN (
            SELECT c2.payer_id, SUM(pm.paid_amount) AS total_paid, 
                   AVG(CASE WHEN pm.payment_date >= c2.submission_date THEN DATEDIFF(pm.payment_date, c2.submission_date) END) AS avg_pmt_latency
            FROM payments pm
            JOIN claims c2 ON pm.claim_id = c2.claim_id
            GROUP BY c2.payer_id
        ) pmt ON py.payer_id = pmt.payer_id
        LEFT JOIN (
            SELECT c3.payer_id, SUM(a.adjustment_amount) AS total_co
            FROM adjustments a
            JOIN claims c3 ON a.claim_id = c3.claim_id
            WHERE a.group_code = 'CO'
            GROUP BY c3.payer_id
        ) adj ON py.payer_id = adj.payer_id
        LEFT JOIN (
            SELECT c4.payer_id, COUNT(i.issue_id) AS issue_count
            FROM issues i
            JOIN claims c4 ON i.claim_id = c4.claim_id
            GROUP BY c4.payer_id
        ) iss ON py.payer_id = iss.payer_id
        {filter_sql}
        GROUP BY py.payer_id, py.payer_reference, py.payer_name, py.payer_type, py.timely_filing_days, pmt.total_paid, pmt.avg_pmt_latency, adj.total_co, iss.issue_count
        HAVING claim_volume > 0
        ORDER BY claim_volume DESC, total_billed DESC, py.payer_id ASC
    """

    rows = execute_analytical_query(conn, sql, tuple(params) if params else None)
    scorecards: List[PayerScorecard] = []

    for r in rows:
        vol = r["claim_volume"]
        billed = quantize_currency(r["total_billed"])
        paid = quantize_currency(r["total_paid"])
        denied_cnt = r["denied_count"]
        timely_cnt = r["timely_count"]
        total_co = quantize_currency(r["total_co"])
        iss_cnt = r["issue_count"]

        pmt_rate = (float(paid) / float(billed) * 100.0) if billed > Decimal("0.00") else 100.0
        den_rate = (float(denied_cnt) / float(vol) * 100.0) if vol > 0 else 0.0
        timely_rate = (float(timely_cnt) / float(vol) * 100.0) if vol > 0 else 100.0
        co_ratio = (float(total_co) / float(billed) * 100.0) if billed > Decimal("0.00") else 0.0

        avg_adj = float(r["avg_adj_latency"]) if r["avg_adj_latency"] is not None else 0.0
        avg_pmt = float(r["avg_pmt_latency"]) if r["avg_pmt_latency"] is not None else 0.0

        scorecards.append(
            PayerScorecard(
                payer_id=r["payer_id"],
                payer_reference=r["payer_reference"],
                payer_name=r["payer_name"],
                payer_type=r["payer_type"],
                claim_volume=vol,
                total_billed=billed,
                total_paid=paid,
                denial_rate=den_rate,
                payment_rate=pmt_rate,
                average_adjudication_latency_days=avg_adj,
                average_payment_latency_days=avg_pmt,
                timely_filing_compliance_rate=timely_rate,
                contractual_adjustment_ratio=co_ratio,
                issue_count=iss_cnt,
            )
        )

    return scorecards

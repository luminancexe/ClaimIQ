"""Financial exposure analytics and reconciliation integrity calculations."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any, List
import pymysql
from analytics.config import AnalyticsConfig
from analytics.models import FinancialExposureSummary
from analytics.database import execute_analytical_query
from generator.financials import quantize_currency

CENT = Decimal("0.01")


def calculate_financial_exposure(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> FinancialExposureSummary:
    """Calculate aggregate financial exposure, variance rollups, and reconciliation rates.

    All monetary values use exact 2-decimal Decimal fixed-point arithmetic.
    """
    if conn is None:
        # Standalone simulated dry-run default
        return FinancialExposureSummary(
            total_billed=Decimal("250000.00"),
            total_paid=Decimal("200000.00"),
            total_contractual_adjustments=Decimal("35000.00"),
            total_patient_responsibility=Decimal("15000.00"),
            total_variance=Decimal("0.00"),
            unreconciled_amount=Decimal("0.00"),
            overpayment_exposure=Decimal("0.00"),
            underpayment_exposure=Decimal("0.00"),
            total_denied_amount=Decimal("0.00"),
            reconciliation_rate=100.00,
            payment_rate=80.00,
            financial_integrity_rate=100.00,
        )

    # 1. Total Billed
    billed_rows = execute_analytical_query(conn, "SELECT COALESCE(SUM(total_billed_amount), 0.00) AS val FROM claims")
    total_billed = quantize_currency(billed_rows[0]["val"])

    # 2. Total Paid
    paid_rows = execute_analytical_query(conn, "SELECT COALESCE(SUM(paid_amount), 0.00) AS val FROM payments")
    total_paid = quantize_currency(paid_rows[0]["val"])

    # 3. Total Contractual Adjustments
    co_rows = execute_analytical_query(conn, "SELECT COALESCE(SUM(adjustment_amount), 0.00) AS val FROM adjustments WHERE group_code = 'CO'")
    total_contractual = quantize_currency(co_rows[0]["val"])

    # 4. Total Patient Responsibility
    pr_rows = execute_analytical_query(conn, "SELECT COALESCE(SUM(total_patient_resp), 0.00) AS val FROM reconciliations")
    total_patient_resp = quantize_currency(pr_rows[0]["val"])

    # 5. Total Variance
    var_rows = execute_analytical_query(conn, "SELECT COALESCE(SUM(variance_amount), 0.00) AS val FROM reconciliations")
    total_variance = quantize_currency(var_rows[0]["val"])

    # 6. Unreconciled Amount
    unrec_rows = execute_analytical_query(conn, "SELECT COALESCE(SUM(total_billed_amount), 0.00) AS val FROM claims WHERE is_reconciled = 0")
    unreconciled_amount = quantize_currency(unrec_rows[0]["val"])

    # 7. Overpayment Exposure
    overpay_sql = """
        SELECT COALESCE(SUM(p.paid_amount - c.total_billed_amount), 0.00) AS val
        FROM payments p
        JOIN claims c ON p.claim_id = c.claim_id
        WHERE p.paid_amount > c.total_billed_amount
    """
    overpay_rows = execute_analytical_query(conn, overpay_sql)
    overpayment_exposure = quantize_currency(overpay_rows[0]["val"])

    # 8. Underpayment / Discrepancy Exposure
    underpay_sql = """
        SELECT COALESCE(SUM(ABS(variance_amount)), 0.00) AS val
        FROM reconciliations
        WHERE variance_amount != 0.00
    """
    underpay_rows = execute_analytical_query(conn, underpay_sql)
    underpayment_exposure = quantize_currency(underpay_rows[0]["val"])

    # 9. Total Denied Amount
    denied_rows = execute_analytical_query(conn, "SELECT COALESCE(SUM(total_billed_amount), 0.00) AS val FROM claims WHERE current_status_code = 'Denied'")
    total_denied_amount = quantize_currency(denied_rows[0]["val"])

    # 10. Reconciliation Rate: (reconciled eligible claims / total eligible claims) * 100
    rec_rate_sql = """
        SELECT 
            COUNT(CASE WHEN is_reconciled = 1 THEN 1 END) AS reconciled_cnt,
            COUNT(*) AS eligible_cnt
        FROM claims
        WHERE current_status_code IN ('Paid', 'Partially Paid', 'Denied')
    """
    rec_rate_rows = execute_analytical_query(conn, rec_rate_sql)
    eligible_cnt = rec_rate_rows[0]["eligible_cnt"]
    reconciled_cnt = rec_rate_rows[0]["reconciled_cnt"]
    reconciliation_rate = (float(reconciled_cnt) / float(eligible_cnt) * 100.0) if eligible_cnt > 0 else 100.0

    # 11. Payment Rate: (total_paid / total_billed) * 100
    payment_rate = (float(total_paid) / float(total_billed) * 100.0) if total_billed > Decimal("0.00") else 100.0

    # 12. Financial Integrity Rate: 100 - (abs_variance / total_billed * 100)
    abs_var_rows = execute_analytical_query(conn, "SELECT COALESCE(SUM(ABS(variance_amount)), 0.00) AS val FROM reconciliations")
    total_abs_variance = quantize_currency(abs_var_rows[0]["val"])

    if total_billed > Decimal("0.00"):
        var_penalty = (float(total_abs_variance) / float(total_billed)) * 100.0
        financial_integrity_rate = max(0.0, 100.0 - var_penalty)
    else:
        financial_integrity_rate = 100.0

    return FinancialExposureSummary(
        total_billed=total_billed,
        total_paid=total_paid,
        total_contractual_adjustments=total_contractual,
        total_patient_responsibility=total_patient_resp,
        total_variance=total_variance,
        unreconciled_amount=unreconciled_amount,
        overpayment_exposure=overpayment_exposure,
        underpayment_exposure=underpayment_exposure,
        total_denied_amount=total_denied_amount,
        reconciliation_rate=reconciliation_rate,
        payment_rate=payment_rate,
        financial_integrity_rate=financial_integrity_rate,
    )

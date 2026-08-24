"""Financial & Reconciliation QA Rules (E023–E033)."""

from decimal import Decimal
from typing import List, Tuple, Any
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord

FINANCIAL_RULES = [
    QARuleDefinition(
        rule_code="R-E023",
        rule_name="Payment Exceeds Total Billed Amount (Overpayment)",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="Critical",
        target_table="payments",
        target_column="paid_amount",
        description="Detects individual payment transactions that exceed the total billed charge on the claim.",
        sql_logic="""
            SELECT p.payment_id, p.payment_reference, p.claim_id, p.paid_amount, c.claim_reference, c.total_billed_amount,
                   (p.paid_amount - c.total_billed_amount) AS variance_val
            FROM payments p
            JOIN claims c ON p.claim_id = c.claim_id
            WHERE p.paid_amount > c.total_billed_amount
        """,
        anomaly_codes=["E023"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E024",
        rule_name="Adjustment Exceeds Total Billed Charge",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="High",
        target_table="adjustments",
        target_column="adjustment_amount",
        description="Detects contractual adjustments or write-offs exceeding the total billed charge of the claim.",
        sql_logic="""
            SELECT a.adjustment_id, a.claim_id, a.adjustment_amount, c.claim_reference, c.total_billed_amount,
                   (a.adjustment_amount - c.total_billed_amount) AS variance_val
            FROM adjustments a
            JOIN claims c ON a.claim_id = c.claim_id
            WHERE a.adjustment_amount > c.total_billed_amount
        """,
        anomaly_codes=["E024"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E025",
        rule_name="Inflated Contractual Write-off Ratio",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="High",
        target_table="adjustments",
        target_column="adjustment_amount",
        description="Detects contractual write-offs that abnormally exceed 95% of total billed charge.",
        sql_logic="""
            SELECT a.adjustment_id, a.claim_id, a.adjustment_amount, c.claim_reference, c.total_billed_amount,
                   (a.adjustment_amount - c.total_billed_amount) AS variance_val
            FROM adjustments a
            JOIN claims c ON a.claim_id = c.claim_id
            WHERE a.group_code = 'CO'
              AND a.adjustment_amount > (c.total_billed_amount * 0.95)
              AND c.total_billed_amount > 0.00
        """,
        anomaly_codes=["E025"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E026",
        rule_name="Reconciliation Patient Responsibility Ledger Discrepancy",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="Medium",
        target_table="reconciliations",
        target_column="total_patient_resp",
        description="Detects reconciliation ledgers where patient responsibility breaks the balance equation.",
        sql_logic="""
            SELECT r.reconciliation_id, r.claim_id, r.total_billed, r.total_paid, r.total_adjustments, r.total_patient_resp,
                   (r.total_billed - (r.total_paid + r.total_adjustments + r.total_patient_resp)) AS variance_val
            FROM reconciliations r
            WHERE (r.total_billed - (r.total_paid + r.total_adjustments + r.total_patient_resp)) != 0.00
              AND r.total_patient_resp > 0.00
        """,
        anomaly_codes=["E026"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E027",
        rule_name="Remittance Header vs Payment Allocation Total Mismatch",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="Critical",
        target_table="remittances",
        target_column="total_paid_amount",
        description="Detects remittance batches where the header paid amount does not equal the sum of child payments.",
        sql_logic="""
            SELECT r.remittance_id, r.remittance_reference, r.total_paid_amount, COALESCE(SUM(p.paid_amount), 0.00) AS sum_pmts,
                   (r.total_paid_amount - COALESCE(SUM(p.paid_amount), 0.00)) AS variance_val
            FROM remittances r
            LEFT JOIN payments p ON r.remittance_id = p.remittance_id
            GROUP BY r.remittance_id, r.remittance_reference, r.total_paid_amount
            HAVING r.total_paid_amount != COALESCE(SUM(p.paid_amount), 0.00)
        """,
        anomaly_codes=["E027"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E028",
        rule_name="Cumulative Claim Overdisbursement",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="Critical",
        target_table="payments",
        target_column="paid_amount",
        description="Detects claims where cumulative payment disbursements exceed the total billed charge.",
        sql_logic="""
            SELECT p.payment_id, p.payment_reference, p.claim_id, p.paid_amount, c.claim_reference, c.total_billed_amount,
                   (p_sum.total_claim_paid - c.total_billed_amount) AS variance_val
            FROM payments p
            JOIN claims c ON p.claim_id = c.claim_id
            JOIN (
                SELECT claim_id, SUM(paid_amount) AS total_claim_paid
                FROM payments
                GROUP BY claim_id
                HAVING SUM(paid_amount) > (SELECT total_billed_amount FROM claims WHERE claims.claim_id = payments.claim_id)
            ) p_sum ON p.claim_id = p_sum.claim_id
        """,
        anomaly_codes=["E028"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E029",
        rule_name="Reconciliation Ledger Non-Zero Variance",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="Critical",
        target_table="reconciliations",
        target_column="variance_amount",
        description="Detects finalized reconciliation ledgers with non-zero financial variance.",
        sql_logic="""
            SELECT r.reconciliation_id, r.claim_id, r.variance_amount, r.reconciliation_status, r.variance_amount AS variance_val
            FROM reconciliations r
            WHERE r.variance_amount != 0.00
        """,
        anomaly_codes=["E029"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E030",
        rule_name="Claim Header Billed vs Line Sum Mismatch",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="Critical",
        target_table="claims",
        target_column="total_billed_amount",
        description="Detects claims where the header billed amount differs from the sum of itemized claim lines.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.total_billed_amount, COALESCE(SUM(cl.line_billed_amount), 0.00) AS line_sum,
                   (c.total_billed_amount - COALESCE(SUM(cl.line_billed_amount), 0.00)) AS variance_val
            FROM claims c
            LEFT JOIN claim_lines cl ON c.claim_id = cl.claim_id
            GROUP BY c.claim_id, c.claim_reference, c.total_billed_amount
            HAVING c.total_billed_amount != COALESCE(SUM(cl.line_billed_amount), 0.00)
        """,
        anomaly_codes=["E030"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E031",
        rule_name="Claim Line Item Arithmetic Calculation Mismatch",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="High",
        target_table="claim_lines",
        target_column="line_billed_amount",
        description="Detects service lines where line_billed_amount != units * unit_price.",
        sql_logic="""
            SELECT cl.claim_line_id, cl.claim_id, cl.line_billed_amount, cl.units, cl.unit_price,
                   (cl.line_billed_amount - ROUND(cl.units * cl.unit_price, 2)) AS variance_val
            FROM claim_lines cl
            WHERE cl.line_billed_amount != ROUND(cl.units * cl.unit_price, 2)
        """,
        anomaly_codes=["E031"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E032",
        rule_name="Zero-Billed Claim with Positive Cash Disbursement",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="High",
        target_table="claims",
        target_column="total_billed_amount",
        description="Detects claims with 0.00 total billed amount that received positive cash payment.",
        sql_logic="""
            SELECT c.claim_id, c.claim_reference, c.total_billed_amount, p.paid_amount AS variance_val
            FROM claims c
            JOIN payments p ON c.claim_id = p.claim_id
            WHERE c.total_billed_amount = 0.00
              AND p.paid_amount > 0.00
        """,
        anomaly_codes=["E032"],
        detection_method="SQL_SET",
    ),
    QARuleDefinition(
        rule_code="R-E033",
        rule_name="Paid Claim Missing Payment Disbursement Record",
        category_code="FINANCIAL",
        category_id=4,
        dimension_code="Financial",
        default_severity_code="High",
        target_table="payments",
        target_column="paid_amount",
        description="Detects claims in Paid status with 0.00 recorded payment or no cash transaction.",
        sql_logic="""
            SELECT p.payment_id, p.payment_reference, p.claim_id, p.paid_amount, c.claim_reference, c.total_billed_amount
            FROM payments p
            JOIN claims c ON p.claim_id = c.claim_id
            WHERE c.current_status_code = 'Paid'
              AND p.paid_amount = 0.00
              AND c.total_billed_amount > 0.00
        """,
        anomaly_codes=["E033"],
        detection_method="SQL_SET",
    ),
]


def evaluate_financial_rule(conn: pymysql.Connection, rule: QARuleDefinition) -> Tuple[int, List[QADetectionRecord]]:
    """Execute a financial SQL rule and collect detection findings."""
    detections: List[QADetectionRecord] = []

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total_count FROM {rule.target_table}")
        records_evaluated = cur.fetchone()["total_count"]

        cur.execute(rule.sql_logic)
        rows = cur.fetchall()

        for r in rows:
            pk_col = f"{rule.target_table[:-1] if rule.target_table.endswith('s') else rule.target_table}_id"
            if rule.target_table == "claim_lines":
                pk_col = "claim_line_id"

            record_id = r.get(pk_col, 0)
            biz_ref = r.get("claim_reference") or r.get("payment_reference") or r.get("remittance_reference") or f"{rule.target_table.upper()}-{record_id}"

            variance = None
            if "variance_val" in r and r["variance_val"] is not None:
                try:
                    variance = float(r["variance_val"])
                except Exception:
                    pass

            claim_id = r.get("claim_id") if "claim_id" in r else (record_id if rule.target_table == "claims" else None)

            det = QADetectionRecord(
                rule_code=rule.rule_code,
                anomaly_code=rule.anomaly_codes[0],
                target_table=rule.target_table,
                target_record_id=record_id,
                target_business_reference=biz_ref,
                target_column=rule.target_column,
                detected_value=str(r.get(rule.target_column)),
                severity_code=rule.default_severity_code,
                dimension_code=rule.dimension_code,
                explanation=f"{rule.rule_name}: financial mismatch on {rule.target_table} ID {record_id}",
                variance_amount=variance,
                claim_id=claim_id,
            )
            detections.append(det)

    return records_evaluated, detections

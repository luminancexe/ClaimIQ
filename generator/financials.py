"""Fixed-point Decimal financial calculations and reconciliation invariants."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List
from generator.random_state import GeneratorRandomState

CENT = Decimal("0.01")


def quantize_currency(amount: Any) -> Decimal:
    """Quantize any numeric value or string to exact 2-decimal fixed point Decimal."""
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_line_billed(units: Decimal, unit_price: Decimal) -> Decimal:
    """Invariant: line_billed_amount = units * unit_price (rounded half up)."""
    return quantize_currency(units * unit_price)


def sum_claim_lines(line_billed_amounts: List[Decimal]) -> Decimal:
    """Invariant: total_billed_amount = sum(line_billed_amounts)."""
    total = sum(line_billed_amounts, Decimal("0.00"))
    return quantize_currency(total)


def calculate_clean_financial_breakdown(
    total_billed: Decimal,
    current_status_code: str,
    rng: GeneratorRandomState
) -> Dict[str, Any]:
    """Calculate mathematically balanced financial values ensuring variance = 0.00.

    Invariant: total_billed = total_paid + total_adjusted + total_patient_resp
    """
    total_billed = quantize_currency(total_billed)

    if current_status_code == "Paid":
        # 80% paid in full directly (zero write-off), 20% paid with standard contracted rate (10-20% CO write-off)
        if rng.random() < 0.60:
            paid_amount = total_billed
            contractual_adj = Decimal("0.00")
            patient_resp = Decimal("0.00")
        else:
            adj_ratio = Decimal(str(round(rng.uniform(0.10, 0.25), 2)))
            contractual_adj = quantize_currency(total_billed * adj_ratio)
            paid_amount = total_billed - contractual_adj
            patient_resp = Decimal("0.00")

        total_adjusted = contractual_adj
        variance = total_billed - (paid_amount + total_adjusted + patient_resp)
        # Ensure zero variance
        paid_amount += variance
        variance = Decimal("0.00")

        adjustments = []
        if contractual_adj > Decimal("0.00"):
            adjustments.append({
                "group_code": "CO",
                "reason_code": "CO-45",
                "adjustment_amount": contractual_adj,
                "adjustment_description": "Contractual fee schedule reduction",
            })

        return {
            "paid_amount": paid_amount,
            "total_paid": paid_amount,
            "total_adjusted": total_adjusted,
            "total_patient_resp": patient_resp,
            "variance_amount": Decimal("0.00"),
            "adjustments": adjustments,
            "denial": None,
            "reconciliation_status": "BALANCED",
            "is_reconciled": True,
        }

    elif current_status_code == "Partially Paid":
        # Contractual adjustment: 15-30%, Patient Copay/Coinsurance: 5-15%
        co_ratio = Decimal(str(round(rng.uniform(0.15, 0.30), 2)))
        pr_ratio = Decimal(str(round(rng.uniform(0.05, 0.15), 2)))

        contractual_adj = quantize_currency(total_billed * co_ratio)
        patient_resp = quantize_currency(total_billed * pr_ratio)
        paid_amount = total_billed - contractual_adj - patient_resp

        if paid_amount < Decimal("0.00"):
            paid_amount = Decimal("0.00")
            contractual_adj = total_billed - patient_resp

        total_adjusted = contractual_adj
        variance = total_billed - (paid_amount + total_adjusted + patient_resp)
        paid_amount += variance

        adjustments = []
        if contractual_adj > Decimal("0.00"):
            adjustments.append({
                "group_code": "CO",
                "reason_code": "CO-45",
                "adjustment_amount": contractual_adj,
                "adjustment_description": "Contractual allowance reduction",
            })
        if patient_resp > Decimal("0.00"):
            adjustments.append({
                "group_code": "PR",
                "reason_code": "PR-1",
                "adjustment_amount": patient_resp,
                "adjustment_description": "Patient deductible / copayment responsibility",
            })

        return {
            "paid_amount": paid_amount,
            "total_paid": paid_amount,
            "total_adjusted": total_adjusted,
            "total_patient_resp": patient_resp,
            "variance_amount": Decimal("0.00"),
            "adjustments": adjustments,
            "denial": None,
            "reconciliation_status": "BALANCED",
            "is_reconciled": True,
        }

    elif current_status_code == "Denied":
        # Zero payment, full balance adjusted under Contractual Obligation or Patient Responsibility
        denial_codes = [
            ("CO-16", "Claim lacks information or has submission defect"),
            ("CO-45", "Charge exceeds fee schedule / maximum allowable amount"),
            ("PR-204", "Service not covered by patient policy benefit"),
            ("CO-97", "Bundled payment reduction / component of another procedure"),
        ]
        chosen_code, chosen_reason = rng.choice(denial_codes)
        group_code = chosen_code.split("-")[0]

        paid_amount = Decimal("0.00")
        total_paid = Decimal("0.00")
        total_adjusted = total_billed if group_code == "CO" else Decimal("0.00")
        total_patient_resp = total_billed if group_code == "PR" else Decimal("0.00")

        adjustments = [{
            "group_code": group_code,
            "reason_code": chosen_code,
            "adjustment_amount": total_billed,
            "adjustment_description": f"Denial balance adjustment: {chosen_reason}",
        }]

        denial = {
            "denial_code": chosen_code,
            "denial_reason": chosen_reason,
            "is_appealable": True,
        }

        return {
            "paid_amount": paid_amount,
            "total_paid": total_paid,
            "total_adjusted": total_adjusted,
            "total_patient_resp": total_patient_resp,
            "variance_amount": Decimal("0.00"),
            "adjustments": adjustments,
            "denial": denial,
            "reconciliation_status": "BALANCED",
            "is_reconciled": True,
        }

    else:
        # In-flight active claims (Submitted, Accepted, Pending, Rejected)
        return {
            "paid_amount": Decimal("0.00"),
            "total_paid": Decimal("0.00"),
            "total_adjusted": Decimal("0.00"),
            "total_patient_resp": Decimal("0.00"),
            "variance_amount": Decimal("0.00"),
            "adjustments": [],
            "denial": None,
            "reconciliation_status": "UNBALANCED",
            "is_reconciled": False,
        }

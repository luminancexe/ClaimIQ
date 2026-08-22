"""Synthetic Electronic Remittance Advice (ERA 835) batch generator."""

from collections import defaultdict
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.identifiers import format_remittance_reference, format_check_trace_number
from generator.dates import format_utc_datetime


def generate_remittances_and_payment_data(
    claims: List[Dict[str, Any]],
    rng: GeneratorRandomState
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Group paid/partially paid claims by payer & remittance date into ERA 835 remittance batches."""
    # Filter for claims with positive payments
    paid_claims = [
        c for c in claims
        if c["current_status_code"] in ("Paid", "Partially Paid") and c["_financials"]["paid_amount"] > Decimal("0.00")
    ]

    # Group by (payer_id, _remit_date)
    batches: Dict[Tuple[int, Any], List[Dict[str, Any]]] = defaultdict(list)
    for c in paid_claims:
        key = (c["payer_id"], c["_remit_date"])
        batches[key].append(c)

    remittances: List[Dict[str, Any]] = []
    payment_specs: List[Dict[str, Any]] = []

    remit_seq = 1
    pmt_seq = 1

    for (payer_id, remit_date), batch_claims in batches.items():
        date_compact = remit_date.strftime("%Y%m%d")
        remit_ref = format_remittance_reference(date_compact, remit_seq)
        pmt_method = "EFT" if rng.random() < 0.90 else "CHECK"
        trace_num = format_check_trace_number(pmt_method, remit_seq)

        batch_total_paid = sum((c["_financials"]["paid_amount"] for c in batch_claims), Decimal("0.00"))
        created_at_str = format_utc_datetime(remit_date, hour=10, minute=0)

        remittance_record = {
            "_remit_ref": remit_ref,
            "payer_id": payer_id,
            "check_trace_number": trace_num,
            "payment_method": pmt_method,
            "total_paid_amount": batch_total_paid,
            "remittance_date": remit_date,
            "created_at": created_at_str,
        }
        remittances.append(remittance_record)

        for c in batch_claims:
            pmt_ref = f"PMT-{c['submission_date'].year}-{pmt_seq:07d}"
            payment_specs.append({
                "payment_reference": pmt_ref,
                "_remit_ref": remit_ref,
                "_claim_ref": c["claim_reference"],
                "paid_amount": c["_financials"]["paid_amount"],
                "payment_date": c["_pmt_date"],
                "created_at": format_utc_datetime(c["_pmt_date"], hour=12, minute=0),
            })
            pmt_seq += 1

        remit_seq += 1

    return remittances, payment_specs


def remittances_to_rows(remittances: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            r["_remit_ref"],
            r["payer_id"],
            r["check_trace_number"],
            r["payment_method"],
            r["total_paid_amount"],
            r["remittance_date"],
            r["created_at"],
        )
        for r in remittances
    ]


REMITTANCES_COLUMNS = [
    "remittance_reference",
    "payer_id",
    "check_trace_number",
    "payment_method",
    "total_paid_amount",
    "remittance_date",
    "created_at",
]

"""Synthetic claim payment transaction mapper."""

from typing import List, Dict, Any, Tuple


def prepare_payment_rows(
    payment_specs: List[Dict[str, Any]],
    remittance_id_map: Dict[str, int],
    claim_id_map: Dict[str, int]
) -> List[Tuple[Any, ...]]:
    """Map remittance_ref and claim_ref to database primary keys and format payment rows."""
    rows: List[Tuple[Any, ...]] = []

    for p in payment_specs:
        remit_id = remittance_id_map[p["_remit_ref"]]
        claim_id = claim_id_map[p["_claim_ref"]]

        rows.append((
            p["payment_reference"],
            remit_id,
            claim_id,
            p["paid_amount"],
            p["payment_date"],
            p["created_at"],
        ))

    return rows


PAYMENTS_COLUMNS = [
    "payment_reference",
    "remittance_id",
    "claim_id",
    "paid_amount",
    "payment_date",
    "created_at",
]

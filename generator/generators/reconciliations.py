"""Synthetic financial reconciliation ledger generator."""

from typing import List, Dict, Any, Tuple
from generator.dates import format_utc_datetime


def prepare_reconciliation_rows(
    claims: List[Dict[str, Any]],
    claim_id_map: Dict[str, int]
) -> List[Tuple[Any, ...]]:
    """Generate financial reconciliation rows for adjudicated claims ensuring exact balance."""
    rows: List[Tuple[Any, ...]] = []

    for c in claims:
        # Populate reconciliation for all claims
        claim_id = claim_id_map[c["claim_reference"]]
        fin = c["_financials"]
        adj_date = c["adjudication_date"] or c["submission_date"]
        reconciled_at = format_utc_datetime(adj_date, hour=17, minute=0)

        rows.append((
            claim_id,
            c["total_billed_amount"],
            fin["total_paid"],
            fin["total_adjusted"],
            fin["total_patient_resp"],
            fin["variance_amount"],
            fin["reconciliation_status"],
            reconciled_at,
        ))

    return rows


RECONCILIATIONS_COLUMNS = [
    "claim_id",
    "total_billed",
    "total_paid",
    "total_adjusted",
    "total_patient_resp",
    "variance_amount",
    "reconciliation_status",
    "reconciled_at",
]

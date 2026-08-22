"""Synthetic claim denial records generator."""

from typing import List, Dict, Any, Tuple
from generator.dates import format_utc_datetime


def prepare_denial_rows(
    claims: List[Dict[str, Any]],
    claim_id_map: Dict[str, int]
) -> List[Tuple[Any, ...]]:
    """Extract denial records from denied claims and format insert tuples."""
    rows: List[Tuple[Any, ...]] = []

    for c in claims:
        if c["current_status_code"] == "Denied":
            claim_id = claim_id_map[c["claim_reference"]]
            denial = c["_financials"].get("denial")
            denial_date = c["adjudication_date"] or c["submission_date"]
            created_at = format_utc_datetime(denial_date, hour=15, minute=0)

            if denial:
                rows.append((
                    claim_id,
                    None,  # Header-level denial
                    denial["denial_code"],
                    denial["denial_reason"],
                    denial_date,
                    1 if denial["is_appealable"] else 0,
                    created_at,
                ))

    return rows


DENIALS_COLUMNS = [
    "claim_id",
    "claim_line_id",
    "denial_code",
    "denial_reason",
    "denial_date",
    "is_appealable",
    "created_at",
]

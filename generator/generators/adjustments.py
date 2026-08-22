"""Synthetic claim adjustments and contractual write-off generator."""

from typing import List, Dict, Any, Tuple


def prepare_adjustment_rows(
    claims: List[Dict[str, Any]],
    claim_id_map: Dict[str, int]
) -> List[Tuple[Any, ...]]:
    """Extract adjustment records from claim financial breakdowns and format insert tuples."""
    rows: List[Tuple[Any, ...]] = []

    for c in claims:
        claim_id = claim_id_map[c["claim_reference"]]
        adjustments = c["_financials"].get("adjustments", [])
        created_at = c["created_at"]

        for adj in adjustments:
            rows.append((
                claim_id,
                None,  # Header-level adjustment
                adj["group_code"],
                adj["reason_code"],
                adj["adjustment_amount"],
                adj["adjustment_description"],
                created_at,
            ))

    return rows


ADJUSTMENTS_COLUMNS = [
    "claim_id",
    "claim_line_id",
    "group_code",
    "reason_code",
    "adjustment_amount",
    "adjustment_description",
    "created_at",
]

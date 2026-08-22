"""Synthetic itemized claim service lines generator and mapper."""

from typing import List, Dict, Any, Tuple


def prepare_claim_line_rows(
    claim_lines: List[Dict[str, Any]],
    claim_id_map: Dict[str, int]
) -> List[Tuple[Any, ...]]:
    """Map in-memory claim_ref to database claim_id and generate insert row tuples."""
    rows: List[Tuple[Any, ...]] = []

    for line in claim_lines:
        claim_id = claim_id_map[line["_claim_ref"]]
        rows.append((
            claim_id,
            line["line_number"],
            line["cpt_code"],
            line["procedure_description"],
            line["units"],
            line["unit_price"],
            line["line_billed_amount"],
            line["line_status"],
            line["created_at"],
        ))

    return rows


CLAIM_LINES_COLUMNS = [
    "claim_id",
    "line_number",
    "cpt_code",
    "procedure_description",
    "units",
    "unit_price",
    "line_billed_amount",
    "line_status",
    "created_at",
]

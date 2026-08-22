"""Synthetic claim lifecycle status transition history generator."""

from datetime import timedelta
from typing import List, Dict, Any, Tuple
from generator.dates import format_utc_datetime


def generate_claim_status_history(
    claims: List[Dict[str, Any]],
    claim_id_map: Dict[str, int]
) -> List[Tuple[Any, ...]]:
    """Generate realistic, valid historical state transitions for each claim."""
    history_rows: List[Tuple[Any, ...]] = []

    for c in claims:
        claim_id = claim_id_map[c["claim_reference"]]
        status = c["current_status_code"]
        sub_date = c["submission_date"]
        adj_date = c["adjudication_date"]

        # Step 1: Initial Submission
        ts1 = format_utc_datetime(sub_date, hour=9, minute=0, second=0)
        history_rows.append((
            claim_id,
            None,
            "Submitted",
            ts1,
            "Electronic claim EDI 837 transmission received",
            "SYSTEM",
        ))

        # Step 2: Front-End Pre-Adjudication Acceptance
        if status in ("Accepted", "Pending", "Paid", "Partially Paid", "Denied"):
            ts2 = format_utc_datetime(sub_date + timedelta(days=1), hour=11, minute=30, second=0)
            history_rows.append((
                claim_id,
                "Submitted",
                "Accepted",
                ts2,
                "Passed front-end clearinghouse syntax edits and payer pre-adjudication",
                "CLEARINGHOUSE_GATEWAY",
            ))

        # Step 3: Secondary Pending Review
        if status == "Pending":
            ts3 = format_utc_datetime(sub_date + timedelta(days=3), hour=14, minute=15, second=0)
            history_rows.append((
                claim_id,
                "Accepted",
                "Pending",
                ts3,
                "Undergoing medical necessity documentation review",
                "PAYER_ADJUDICATOR",
            ))

        # Step 4: Final Adjudication (Paid, Partially Paid, Denied)
        if status in ("Paid", "Partially Paid", "Denied") and adj_date:
            ts_final = format_utc_datetime(adj_date, hour=16, minute=45, second=0)
            reason = f"Final adjudication determination reached: {status}"
            history_rows.append((
                claim_id,
                "Accepted",
                status,
                ts_final,
                reason,
                "PAYER_ADJUDICATOR",
            ))

    return history_rows


CLAIM_STATUS_HISTORY_COLUMNS = [
    "claim_id",
    "previous_status_code",
    "new_status_code",
    "transition_timestamp",
    "transition_reason",
    "actor_reference",
]

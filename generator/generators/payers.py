"""Synthetic healthcare payer organization generator."""

from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.identifiers import format_payer_reference
from generator.templates.payer_profiles import SYNTHETIC_PAYERS
from generator.dates import format_utc_datetime


def generate_payers(count: int, rng: GeneratorRandomState) -> List[Dict[str, Any]]:
    """Generate synthetic payer master entities conforming to target distribution."""
    payers: List[Dict[str, Any]] = []

    for i in range(1, count + 1):
        ref = format_payer_reference(i)
        template = SYNTHETIC_PAYERS[(i - 1) % len(SYNTHETIC_PAYERS)]
        # If count exceeds templates, append regional suffix
        suffix = f" - Region {(i - 1) // len(SYNTHETIC_PAYERS) + 1}" if i > len(SYNTHETIC_PAYERS) else ""
        payer_name = f"{template['name']}{suffix}"
        created_at = format_utc_datetime(rng.faker.date_time_between(start_date="-4y", end_date="-2y"))

        payers.append({
            "payer_reference": ref,
            "payer_name": payer_name,
            "payer_type": template["type"],
            "timely_filing_days": template["timely_filing_days"],
            "created_at": created_at,
            "updated_at": created_at,
            "_raw_template_plans": template["plans"],
        })

    return payers


def payers_to_rows(payers: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            p["payer_reference"],
            p["payer_name"],
            p["payer_type"],
            p["timely_filing_days"],
            p["created_at"],
            p["updated_at"],
        )
        for p in payers
    ]


PAYERS_COLUMNS = [
    "payer_reference",
    "payer_name",
    "payer_type",
    "timely_filing_days",
    "created_at",
    "updated_at",
]

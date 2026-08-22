"""Synthetic healthcare facility generator."""

from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.identifiers import format_facility_reference
from generator.templates.provider_profiles import FACILITY_TEMPLATES
from generator.dates import format_utc_datetime


def generate_facilities(count: int, rng: GeneratorRandomState) -> List[Dict[str, Any]]:
    """Generate synthetic healthcare facility master records."""
    facilities: List[Dict[str, Any]] = []

    for i in range(1, count + 1):
        ref = format_facility_reference(i)
        template = FACILITY_TEMPLATES[(i - 1) % len(FACILITY_TEMPLATES)]
        city_name = rng.faker.city()
        facility_name = f"{city_name} {template['name_suffix']}"
        tin = f"{rng.randint(10, 99)}-{rng.randint(1000000, 9999999)}"
        state = rng.state_abbr()
        created_at = format_utc_datetime(rng.faker.date_time_between(start_date="-3y", end_date="-1y"))

        facilities.append({
            "facility_reference": ref,
            "facility_name": facility_name,
            "tin": tin,
            "facility_type": template["facility_type"],
            "state": state,
            "created_at": created_at,
            "updated_at": created_at,
        })

    return facilities


def facilities_to_rows(facilities: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    """Convert facility dicts into database insert row tuples."""
    return [
        (
            f["facility_reference"],
            f["facility_name"],
            f["tin"],
            f["facility_type"],
            f["state"],
            f["created_at"],
            f["updated_at"],
        )
        for f in facilities
    ]


FACILITIES_COLUMNS = [
    "facility_reference",
    "facility_name",
    "tin",
    "facility_type",
    "state",
    "created_at",
    "updated_at",
]

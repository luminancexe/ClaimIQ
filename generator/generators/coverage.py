"""Synthetic patient health insurance policy coverage generator."""

from datetime import date
from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.identifiers import format_member_id
from generator.dates import generate_coverage_dates, format_utc_datetime


def generate_patient_coverages(
    patients: List[Dict[str, Any]],
    patient_id_map: Dict[str, int],
    plan_ids: List[int],
    config_start: date,
    config_end: date,
    rng: GeneratorRandomState
) -> List[Dict[str, Any]]:
    """Generate primary (and occasional secondary) insurance coverage for each patient."""
    coverages: List[Dict[str, Any]] = []
    member_seq = 1

    for p in patients:
        patient_id = patient_id_map[p["patient_reference"]]
        dob = p["date_of_birth"]
        plan_id = rng.choice(plan_ids)
        effective_date, termination_date = generate_coverage_dates(rng, dob, config_start, config_end)
        group_num = f"GRP-{rng.randint(10000, 99999)}"
        created_at = format_utc_datetime(rng.faker.date_time_between(start_date="-2y", end_date="-1y"))

        coverages.append({
            "patient_id": patient_id,
            "plan_id": plan_id,
            "member_id": format_member_id(member_seq),
            "group_number": group_num,
            "effective_date": effective_date,
            "termination_date": termination_date,
            "is_primary": True,
            "created_at": created_at,
            "_patient_ref": p["patient_reference"],
            "_dob": dob,
        })
        member_seq += 1

    return coverages


def coverages_to_rows(coverages: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            c["patient_id"],
            c["plan_id"],
            c["member_id"],
            c["group_number"],
            c["effective_date"],
            c["termination_date"],
            1 if c["is_primary"] else 0,
            c["created_at"],
        )
        for c in coverages
    ]


COVERAGE_COLUMNS = [
    "patient_id",
    "plan_id",
    "member_id",
    "group_number",
    "effective_date",
    "termination_date",
    "is_primary",
    "created_at",
]

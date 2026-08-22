"""Synthetic patient demographics generator."""

from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.identifiers import format_patient_reference
from generator.dates import generate_patient_dob, format_utc_datetime
from generator.distributions import sample_gender


def generate_patients(count: int, rng: GeneratorRandomState) -> List[Dict[str, Any]]:
    """Generate synthetic adult patient master records (18-85 years old)."""
    patients: List[Dict[str, Any]] = []

    for i in range(1, count + 1):
        ref = format_patient_reference(i)
        gender = sample_gender(rng)
        first_name = rng.first_name(gender=gender)
        last_name = rng.last_name()
        dob = generate_patient_dob(rng, min_age=18, max_age=85)
        state = rng.state_abbr()
        created_at = format_utc_datetime(rng.faker.date_time_between(start_date="-3y", end_date="-1y"))

        patients.append({
            "patient_reference": ref,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob,
            "gender": gender,
            "address_state": state,
            "created_at": created_at,
            "updated_at": created_at,
        })

    return patients


def patients_to_rows(patients: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            p["patient_reference"],
            p["first_name"],
            p["last_name"],
            p["date_of_birth"],
            p["gender"],
            p["address_state"],
            p["created_at"],
            p["updated_at"],
        )
        for p in patients
    ]


PATIENTS_COLUMNS = [
    "patient_reference",
    "first_name",
    "last_name",
    "date_of_birth",
    "gender",
    "address_state",
    "created_at",
    "updated_at",
]

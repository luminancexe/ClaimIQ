"""Synthetic encounter ICD-10 diagnosis generator."""

from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.templates.clinical_codes import ICD10_CODES
from generator.distributions import sample_diagnoses_count
from generator.dates import format_utc_datetime


def generate_encounter_diagnoses(
    encounters: List[Dict[str, Any]],
    encounter_id_map: Dict[str, int],
    rng: GeneratorRandomState
) -> List[Dict[str, Any]]:
    """Generate 1-3 diagnosis codes per encounter with sequence numbers and exactly 1 primary."""
    diagnoses: List[Dict[str, Any]] = []

    for enc in encounters:
        enc_id = encounter_id_map[enc["encounter_reference"]]
        num_diags = sample_diagnoses_count(rng)
        chosen_codes = rng.sample(ICD10_CODES, min(num_diags, len(ICD10_CODES)))
        created_at = enc["created_at"]

        for seq, item in enumerate(chosen_codes, start=1):
            diagnoses.append({
                "encounter_id": enc_id,
                "icd10_code": item["code"],
                "diagnosis_description": item["description"],
                "is_primary": (seq == 1),
                "sequence_number": seq,
                "created_at": created_at,
            })

    return diagnoses


def diagnoses_to_rows(diagnoses: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            d["encounter_id"],
            d["icd10_code"],
            d["diagnosis_description"],
            1 if d["is_primary"] else 0,
            d["sequence_number"],
            d["created_at"],
        )
        for d in diagnoses
    ]


DIAGNOSES_COLUMNS = [
    "encounter_id",
    "icd10_code",
    "diagnosis_description",
    "is_primary",
    "sequence_number",
    "created_at",
]

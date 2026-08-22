"""Synthetic clinical encounter generator."""

from datetime import date
from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.identifiers import format_encounter_reference
from generator.dates import generate_encounter_dates, format_utc_datetime
from generator.distributions import sample_encounter_type


def generate_encounters(
    count: int,
    coverages: List[Dict[str, Any]],
    providers: List[Dict[str, Any]],
    provider_id_map: Dict[str, int],
    facility_id_map: Dict[str, int],
    config_start: date,
    config_end: date,
    rng: GeneratorRandomState
) -> List[Dict[str, Any]]:
    """Generate clinical encounters ensuring DOS falls within valid active coverage."""
    encounters: List[Dict[str, Any]] = []

    for i in range(1, count + 1):
        ref = format_encounter_reference(i)
        cov = rng.choice(coverages)
        patient_id = cov["patient_id"]
        
        prov_dict = rng.choice(providers)
        provider_id = provider_id_map[prov_dict["provider_reference"]]
        facility_id = prov_dict["facility_id"]

        enc_type = sample_encounter_type(rng)
        dos, discharge_date = generate_encounter_dates(
            rng,
            coverage_effective=cov["effective_date"],
            coverage_term=cov["termination_date"],
            config_start=config_start,
            config_end=config_end,
            encounter_type=enc_type,
        )

        created_at = format_utc_datetime(dos, hour=18, minute=30)

        encounters.append({
            "encounter_reference": ref,
            "patient_id": patient_id,
            "provider_id": provider_id,
            "facility_id": facility_id,
            "date_of_service": dos,
            "encounter_type": enc_type,
            "discharge_date": discharge_date,
            "created_at": created_at,
            "updated_at": created_at,
            "_plan_id": cov["plan_id"],
        })

    return encounters


def encounters_to_rows(encounters: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            e["encounter_reference"],
            e["patient_id"],
            e["provider_id"],
            e["facility_id"],
            e["date_of_service"],
            e["encounter_type"],
            e["discharge_date"],
            e["created_at"],
            e["updated_at"],
        )
        for e in encounters
    ]


ENCOUNTERS_COLUMNS = [
    "encounter_reference",
    "patient_id",
    "provider_id",
    "facility_id",
    "date_of_service",
    "encounter_type",
    "discharge_date",
    "created_at",
    "updated_at",
]

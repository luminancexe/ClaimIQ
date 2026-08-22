"""Synthetic healthcare clinician and rendering provider generator."""

from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.identifiers import format_provider_reference, generate_npi
from generator.templates.provider_profiles import PROVIDER_SPECIALTIES
from generator.dates import format_utc_datetime


def generate_providers(
    count: int,
    facility_ids: List[int],
    rng: GeneratorRandomState
) -> List[Dict[str, Any]]:
    """Generate synthetic providers with unique Luhn-valid NPIs linked to facilities."""
    providers: List[Dict[str, Any]] = []

    for i in range(1, count + 1):
        ref = format_provider_reference(i)
        gender = rng.choice(["M", "F"])
        first_name = rng.first_name(gender=gender)
        last_name = rng.last_name()
        npi = generate_npi(i, prefix_digit=1)
        
        spec_profile = PROVIDER_SPECIALTIES[(i - 1) % len(PROVIDER_SPECIALTIES)]
        facility_id = rng.choice(facility_ids)
        created_at = format_utc_datetime(rng.faker.date_time_between(start_date="-3y", end_date="-1y"))

        providers.append({
            "provider_reference": ref,
            "facility_id": facility_id,
            "first_name": first_name,
            "last_name": last_name,
            "npi": npi,
            "taxonomy_code": spec_profile["taxonomy_code"],
            "specialty": spec_profile["specialty"],
            "created_at": created_at,
            "updated_at": created_at,
        })

    return providers


def providers_to_rows(providers: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            p["provider_reference"],
            p["facility_id"],
            p["first_name"],
            p["last_name"],
            p["npi"],
            p["taxonomy_code"],
            p["specialty"],
            p["created_at"],
            p["updated_at"],
        )
        for p in providers
    ]


PROVIDERS_COLUMNS = [
    "provider_reference",
    "facility_id",
    "first_name",
    "last_name",
    "npi",
    "taxonomy_code",
    "specialty",
    "created_at",
    "updated_at",
]

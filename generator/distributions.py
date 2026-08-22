"""Statistical and categorical distributions for realistic synthetic healthcare data."""

from typing import List, Tuple
from generator.random_state import GeneratorRandomState

# Payer Types: Commercial (60%), Medicare (25%), Medicaid (15%)
PAYER_TYPE_DISTRIBUTION: List[Tuple[str, float]] = [
    ("Commercial", 0.60),
    ("Medicare", 0.25),
    ("Medicaid", 0.15),
]

# Clean Baseline Claim Current Status Distribution
# Paid: 75%, Partially Paid: 15%, Denied: 7%, Active/In-Flight: 3% (Submitted: 1%, Accepted: 1%, Pending: 1%)
CLAIM_STATUS_DISTRIBUTION: List[Tuple[str, float]] = [
    ("Paid", 0.75),
    ("Partially Paid", 0.15),
    ("Denied", 0.07),
    ("Submitted", 0.01),
    ("Accepted", 0.01),
    ("Pending", 0.01),
]

# Lines Per Claim Distribution (1 to 5 lines)
LINES_PER_CLAIM_DISTRIBUTION: List[Tuple[int, float]] = [
    (1, 0.40),
    (2, 0.30),
    (3, 0.15),
    (4, 0.10),
    (5, 0.05),
]

# Diagnoses Per Encounter Distribution (1 to 3 diagnoses)
DIAGNOSES_PER_ENCOUNTER_DISTRIBUTION: List[Tuple[int, float]] = [
    (1, 0.50),
    (2, 0.35),
    (3, 0.15),
]

# Encounter Types
ENCOUNTER_TYPE_DISTRIBUTION: List[Tuple[str, float]] = [
    ("Outpatient Office Visit", 0.60),
    ("Specialist Consult", 0.20),
    ("Diagnostic Lab/Imaging", 0.10),
    ("Urgent Care", 0.06),
    ("Inpatient Hospital", 0.04),
]

# Gender Distribution
GENDER_DISTRIBUTION: List[Tuple[str, float]] = [
    ("F", 0.52),
    ("M", 0.48),
]


def sample_categorical(rng: GeneratorRandomState, dist: List[Tuple[any, float]]) -> any:
    """Sample a single item from a categorical distribution (item, weight)."""
    items = [item for item, weight in dist]
    weights = [weight for item, weight in dist]
    return rng.choices(items, weights=weights, k=1)[0]


def sample_payer_type(rng: GeneratorRandomState) -> str:
    return sample_categorical(rng, PAYER_TYPE_DISTRIBUTION)


def sample_claim_status(rng: GeneratorRandomState) -> str:
    return sample_categorical(rng, CLAIM_STATUS_DISTRIBUTION)


def sample_lines_count(rng: GeneratorRandomState) -> int:
    return sample_categorical(rng, LINES_PER_CLAIM_DISTRIBUTION)


def sample_diagnoses_count(rng: GeneratorRandomState) -> int:
    return sample_categorical(rng, DIAGNOSES_PER_ENCOUNTER_DISTRIBUTION)


def sample_encounter_type(rng: GeneratorRandomState) -> str:
    return sample_categorical(rng, ENCOUNTER_TYPE_DISTRIBUTION)


def sample_gender(rng: GeneratorRandomState) -> str:
    return sample_categorical(rng, GENDER_DISTRIBUTION)

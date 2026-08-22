"""Synthetic health insurance plan product generator."""

from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.dates import format_utc_datetime


def generate_insurance_plans(
    payers: List[Dict[str, Any]],
    payer_id_map: Dict[str, int],
    target_plan_count: int,
    rng: GeneratorRandomState
) -> List[Dict[str, Any]]:
    """Generate insurance plans distributed across generated payers."""
    plans: List[Dict[str, Any]] = []
    plan_seq = 1

    # First pass: ensure every payer gets their baseline plans from template
    for p in payers:
        payer_id = payer_id_map[p["payer_reference"]]
        raw_plans = p.get("_raw_template_plans", [])
        for rp in raw_plans:
            created_at = format_utc_datetime(rng.faker.date_time_between(start_date="-3y", end_date="-1y"))
            plans.append({
                "_plan_seq": plan_seq,
                "payer_id": payer_id,
                "plan_name": rp["name"],
                "plan_type": rp["type"],
                "created_at": created_at,
            })
            plan_seq += 1

    # Second pass: if target_plan_count > current plans, generate additional variants
    while len(plans) < target_plan_count:
        p = rng.choice(payers)
        payer_id = payer_id_map[p["payer_reference"]]
        tier = rng.choice(["Select", "Choice", "Premier", "Essential", "Optima"])
        plan_type = rng.choice(["PPO", "HMO", "EPO", "POS", "HDHP"])
        plan_name = f"{p['payer_name']} {tier} {plan_type} {rng.randint(100, 999)}"
        created_at = format_utc_datetime(rng.faker.date_time_between(start_date="-2y", end_date="-1y"))

        plans.append({
            "_plan_seq": plan_seq,
            "payer_id": payer_id,
            "plan_name": plan_name,
            "plan_type": plan_type,
            "created_at": created_at,
        })
        plan_seq += 1

    return plans


def plans_to_rows(plans: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            p["payer_id"],
            p["plan_name"],
            p["plan_type"],
            p["created_at"],
        )
        for p in plans
    ]


PLANS_COLUMNS = [
    "payer_id",
    "plan_name",
    "plan_type",
    "created_at",
]

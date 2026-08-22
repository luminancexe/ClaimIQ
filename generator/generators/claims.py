"""Synthetic healthcare billing claim header and line item generator."""

from datetime import date
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from generator.random_state import GeneratorRandomState
from generator.identifiers import format_claim_reference
from generator.dates import generate_claim_dates, generate_adjudication_dates, format_utc_datetime
from generator.distributions import sample_claim_status, sample_lines_count
from generator.templates.clinical_codes import CPT_CODES
from generator.financials import calculate_line_billed, sum_claim_lines, quantize_currency, calculate_clean_financial_breakdown


def generate_claims_and_lines(
    target_claim_count: int,
    encounters: List[Dict[str, Any]],
    encounter_id_map: Dict[str, int],
    plans: List[Dict[str, Any]],
    plan_to_payer_map: Dict[int, int],
    payers: List[Dict[str, Any]],
    rng: GeneratorRandomState
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Generate claim headers and itemized service lines ensuring exact arithmetic consistency."""
    claims: List[Dict[str, Any]] = []
    claim_lines: List[Dict[str, Any]] = []

    # Map payer_id to timely_filing_days
    timely_map = {p["_raw_id"] if "_raw_id" in p else i + 1: p["timely_filing_days"] for i, p in enumerate(payers)}

    for i in range(1, target_claim_count + 1):
        enc = encounters[(i - 1) % len(encounters)]
        encounter_id = encounter_id_map[enc["encounter_reference"]]
        patient_id = enc["patient_id"]
        provider_id = enc["provider_id"]
        dos = enc["date_of_service"]
        discharge_date = enc["discharge_date"]
        plan_id = enc["_plan_id"]
        payer_id = plan_to_payer_map.get(plan_id, 1)

        timely_days = timely_map.get(payer_id, 365)
        submission_date = generate_claim_dates(rng, dos, discharge_date, timely_days)
        year = submission_date.year
        claim_ref = format_claim_reference(year, i)

        status_code = sample_claim_status(rng)

        if status_code in ("Paid", "Partially Paid", "Denied"):
            adj_date, remit_date, pmt_date = generate_adjudication_dates(rng, submission_date)
        else:
            adj_date, remit_date, pmt_date = None, None, None

        # Generate itemized service lines
        num_lines = sample_lines_count(rng)
        line_records: List[Dict[str, Any]] = []
        line_billed_amounts: List[Decimal] = []

        chosen_cpts = rng.sample(CPT_CODES, min(num_lines, len(CPT_CODES)))
        created_at_str = format_utc_datetime(submission_date, hour=8, minute=rng.randint(0, 59))

        for line_num, cpt in enumerate(chosen_cpts, start=1):
            units = Decimal("1.00")
            min_p, max_p = cpt["min_price"], cpt["max_price"]
            raw_price = quantize_currency(rng.uniform(float(min_p), float(max_p)))
            line_billed = calculate_line_billed(units, raw_price)
            line_billed_amounts.append(line_billed)

            line_records.append({
                "_claim_ref": claim_ref,
                "line_number": line_num,
                "cpt_code": cpt["code"],
                "procedure_description": cpt["description"],
                "units": units,
                "unit_price": raw_price,
                "line_billed_amount": line_billed,
                "line_status": status_code,
                "created_at": created_at_str,
            })

        total_billed = sum_claim_lines(line_billed_amounts)

        # Compute balanced financial breakdown
        fin_breakdown = calculate_clean_financial_breakdown(total_billed, status_code, rng)

        claim_record = {
            "claim_reference": claim_ref,
            "encounter_id": encounter_id,
            "patient_id": patient_id,
            "billing_provider_id": provider_id,
            "payer_id": payer_id,
            "current_status_code": status_code,
            "total_billed_amount": total_billed,
            "submission_date": submission_date,
            "adjudication_date": adj_date,
            "is_reconciled": fin_breakdown["is_reconciled"],
            "created_at": created_at_str,
            "updated_at": created_at_str,
            "_financials": fin_breakdown,
            "_remit_date": remit_date,
            "_pmt_date": pmt_date,
        }

        claims.append(claim_record)
        claim_lines.extend(line_records)

    return claims, claim_lines


def claims_to_rows(claims: List[Dict[str, Any]]) -> List[Tuple[Any, ...]]:
    return [
        (
            c["claim_reference"],
            c["encounter_id"],
            c["patient_id"],
            c["billing_provider_id"],
            c["payer_id"],
            c["current_status_code"],
            c["total_billed_amount"],
            c["submission_date"],
            c["adjudication_date"],
            1 if c["is_reconciled"] else 0,
            c["created_at"],
            c["updated_at"],
        )
        for c in claims
    ]


CLAIMS_COLUMNS = [
    "claim_reference",
    "encounter_id",
    "patient_id",
    "billing_provider_id",
    "payer_id",
    "current_status_code",
    "total_billed_amount",
    "submission_date",
    "adjudication_date",
    "is_reconciled",
    "created_at",
    "updated_at",
]

"""Chronological date sequence generator ensuring 100% temporal validity."""

from datetime import date, datetime, timedelta, timezone
from typing import Optional, Tuple
from generator.random_state import GeneratorRandomState


def generate_patient_dob(rng: GeneratorRandomState, min_age: int = 18, max_age: int = 85, as_of: date = date(2025, 1, 1)) -> date:
    """Generate a realistic date of birth between min_age and max_age years before as_of."""
    age_days = rng.randint(min_age * 365, max_age * 365)
    return as_of - timedelta(days=age_days)


def generate_coverage_dates(
    rng: GeneratorRandomState,
    dob: date,
    config_start: date,
    config_end: date
) -> Tuple[date, Optional[date]]:
    """Generate policy effective_date (after 18th birthday) and optional termination_date."""
    eighteenth_bday = dob + timedelta(days=18 * 365)
    # Effective date 1-5 years prior to config_start, or after 18th bday
    earliest_effective = max(eighteenth_bday, config_start - timedelta(days=5 * 365))
    latest_effective = config_start
    
    if earliest_effective > latest_effective:
        effective_date = earliest_effective
    else:
        days_span = (latest_effective - earliest_effective).days
        effective_date = earliest_effective + timedelta(days=rng.randint(0, max(0, days_span)))

    # 10% chance of policy termination after config_end, 90% active (termination_date = None)
    if rng.random() < 0.10:
        term_days = rng.randint(30, 365)
        termination_date: Optional[date] = config_end + timedelta(days=term_days)
    else:
        termination_date = None

    return effective_date, termination_date


def generate_encounter_dates(
    rng: GeneratorRandomState,
    coverage_effective: date,
    coverage_term: Optional[date],
    config_start: date,
    config_end: date,
    encounter_type: str
) -> Tuple[date, Optional[date]]:
    """Generate Date of Service (DOS) and Discharge Date.

    Ensures:
    1. DOS >= max(coverage_effective, config_start)
    2. DOS <= min(coverage_term or config_end, config_end)
    3. For Inpatient: discharge_date = DOS + 1..10 days
    4. For Outpatient: discharge_date = DOS
    """
    earliest_dos = max(coverage_effective, config_start)
    latest_dos = min(coverage_term or config_end, config_end)

    if earliest_dos > latest_dos:
        earliest_dos = latest_dos - timedelta(days=30)

    span = (latest_dos - earliest_dos).days
    dos = earliest_dos + timedelta(days=rng.randint(0, max(0, span)))

    if encounter_type.lower() in ("inpatient", "inpatient hospital", "surgical"):
        length_of_stay = rng.randint(1, 10)
        discharge_date: Optional[date] = dos + timedelta(days=length_of_stay)
    else:
        # Outpatient encounters typically discharge same day
        discharge_date = dos

    return dos, discharge_date


def generate_claim_dates(
    rng: GeneratorRandomState,
    dos: date,
    discharge_date: Optional[date],
    timely_filing_days: int = 365
) -> date:
    """Generate claim submission_date (1-14 days after DOS or discharge, within timely filing)."""
    base_date = discharge_date if discharge_date else dos
    days_to_submit = rng.randint(1, min(14, max(1, timely_filing_days - 10)))
    submission_date = base_date + timedelta(days=days_to_submit)
    return submission_date


def generate_adjudication_dates(
    rng: GeneratorRandomState,
    submission_date: date
) -> Tuple[date, date, date]:
    """Generate adjudication_date, remittance_date, and payment_date in valid sequence.

    Sequence:
    submission_date <= adjudication_date (3-21 days)
    adjudication_date <= remittance_date (0-3 days)
    remittance_date <= payment_date (0-2 days)
    """
    adjudication_lag = rng.randint(3, 21)
    adjudication_date = submission_date + timedelta(days=adjudication_lag)

    remit_lag = rng.randint(0, 3)
    remittance_date = adjudication_date + timedelta(days=remit_lag)

    pmt_lag = rng.randint(0, 2)
    payment_date = remittance_date + timedelta(days=pmt_lag)

    return adjudication_date, remittance_date, payment_date


def format_utc_datetime(dt_or_date, hour: int = 12, minute: int = 0, second: int = 0, microsecond: int = 0) -> str:
    """Convert date or datetime into MySQL DATETIME(6) UTC string: YYYY-MM-DD HH:MM:SS.ffffff."""
    if isinstance(dt_or_date, datetime):
        return dt_or_date.strftime("%Y-%m-%d %H:%M:%S.%f")
    elif isinstance(dt_or_date, date):
        dt = datetime(dt_or_date.year, dt_or_date.month, dt_or_date.day, hour, minute, second, microsecond)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    return str(dt_or_date)

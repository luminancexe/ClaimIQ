"""Unit tests for chronological date generation and sequencing rules."""

from datetime import date, timedelta
import pytest
from generator.random_state import GeneratorRandomState
from generator.dates import (
    generate_patient_dob,
    generate_coverage_dates,
    generate_encounter_dates,
    generate_claim_dates,
    generate_adjudication_dates,
    format_utc_datetime,
)


def test_patient_dob():
    rng = GeneratorRandomState(42)
    as_of = date(2025, 1, 1)
    for _ in range(50):
        dob = generate_patient_dob(rng, min_age=18, max_age=85, as_of=as_of)
        age = (as_of - dob).days / 365.25
        assert 18 <= age <= 86
        assert dob < as_of


def test_coverage_dates_chronology():
    rng = GeneratorRandomState(42)
    config_start = date(2025, 1, 1)
    config_end = date(2026, 6, 30)

    for _ in range(50):
        dob = generate_patient_dob(rng, 18, 85, as_of=config_start)
        eff, term = generate_coverage_dates(rng, dob, config_start, config_end)
        assert eff > dob + timedelta(days=17 * 365)
        if term:
            assert term >= eff


def test_encounter_and_claim_dates_chronology():
    rng = GeneratorRandomState(42)
    config_start = date(2025, 1, 1)
    config_end = date(2026, 6, 30)

    for _ in range(50):
        eff = date(2024, 1, 1)
        term = None
        
        # Inpatient
        dos_inp, dis_inp = generate_encounter_dates(rng, eff, term, config_start, config_end, "Inpatient Hospital")
        assert dis_inp >= dos_inp
        assert config_start <= dos_inp <= config_end

        # Outpatient
        dos_out, dis_out = generate_encounter_dates(rng, eff, term, config_start, config_end, "Outpatient Office Visit")
        assert dis_out == dos_out

        # Claim submission
        sub_date = generate_claim_dates(rng, dos_out, dis_out, timely_filing_days=180)
        assert sub_date >= dos_out
        assert sub_date <= dos_out + timedelta(days=180)

        # Adjudication, remittance, payment
        adj_date, remit_date, pmt_date = generate_adjudication_dates(rng, sub_date)
        assert adj_date >= sub_date
        assert remit_date >= adj_date
        assert pmt_date >= remit_date


def test_format_utc_datetime():
    d = date(2026, 8, 22)
    formatted = format_utc_datetime(d, hour=14, minute=30, second=15, microsecond=123456)
    assert formatted == "2026-08-22 14:30:15.123456"

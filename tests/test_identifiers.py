"""Unit tests for identifier formatting and NPI Luhn generation/validation."""

import pytest
from generator.identifiers import (
    format_patient_reference,
    format_facility_reference,
    format_provider_reference,
    format_payer_reference,
    format_member_id,
    format_encounter_reference,
    format_claim_reference,
    format_remittance_reference,
    format_payment_reference,
    format_issue_reference,
    generate_npi,
    validate_npi,
)


def test_business_reference_formats():
    assert format_patient_reference(1) == "PAT-0000001"
    assert format_patient_reference(9999999) == "PAT-9999999"
    assert format_facility_reference(5) == "FAC-0005"
    assert format_provider_reference(12) == "PRV-00012"
    assert format_payer_reference(3) == "PAY-003"
    assert format_member_id(42) == "MEM-00000042"
    assert format_encounter_reference(100) == "ENC-00000100"
    assert format_claim_reference(2026, 1) == "CLM-2026-0000001"
    assert format_remittance_reference("20260822", 1) == "REM-20260822-0001"
    assert format_payment_reference(2026, 50) == "PMT-2026-0000050"
    assert format_issue_reference(7) == "ISS-000007"


def test_npi_generation_and_validation():
    # Test generation of 100 consecutive deterministic NPIs
    for seq in range(1, 101):
        npi = generate_npi(seq)
        assert len(npi) == 10
        assert npi.isdigit()
        assert validate_npi(npi) is True

    # Test invalid NPI strings
    assert validate_npi("123456789") is False  # 9 digits
    assert validate_npi("12345678901") is False  # 11 digits
    assert validate_npi("123456789A") is False  # non-digit
    assert validate_npi("") is False
    assert validate_npi(None) is False

    # Test known corrupted check digit
    valid_npi = generate_npi(1)
    corrupted_check = "0" if valid_npi[-1] != "0" else "1"
    invalid_npi = valid_npi[:-1] + corrupted_check
    assert validate_npi(invalid_npi) is False

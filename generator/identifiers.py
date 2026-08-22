"""Deterministic business reference formatting and NPI Luhn generation/validation."""

import re
from typing import Optional


def format_patient_reference(seq: int) -> str:
    """Format: PAT-0000001 (7 digits)."""
    return f"PAT-{seq:07d}"


def format_facility_reference(seq: int) -> str:
    """Format: FAC-0001 (4 digits)."""
    return f"FAC-{seq:04d}"


def format_provider_reference(seq: int) -> str:
    """Format: PRV-00001 (5 digits)."""
    return f"PRV-{seq:05d}"


def format_payer_reference(seq: int) -> str:
    """Format: PAY-001 (3 digits)."""
    return f"PAY-{seq:03d}"


def format_member_id(seq: int) -> str:
    """Format: MEM-00000001 (8 digits)."""
    return f"MEM-{seq:08d}"


def format_encounter_reference(seq: int) -> str:
    """Format: ENC-00000001 (8 digits)."""
    return f"ENC-{seq:08d}"


def format_claim_reference(year: int, seq: int) -> str:
    """Format: CLM-YYYY-0000001 (7 digits)."""
    return f"CLM-{year}-{seq:07d}"


def format_remittance_reference(date_compact: str, seq: int) -> str:
    """Format: REM-YYYYMMDD-0001 (4 digits)."""
    return f"REM-{date_compact}-{seq:04d}"


def format_check_trace_number(payment_method: str, seq: int) -> str:
    """Format: EFT-000000001 or CHK-000000001 (9 digits)."""
    prefix = "EFT" if payment_method == "EFT" else "CHK"
    return f"{prefix}-{seq:09d}"


def format_payment_reference(year: int, seq: int) -> str:
    """Format: PMT-YYYY-0000001 (7 digits)."""
    return f"PMT-{year}-{seq:07d}"


def format_issue_reference(seq: int) -> str:
    """Format: ISS-000001 (6 digits)."""
    return f"ISS-{seq:06d}"


def format_run_reference(date_compact: str, seq: int) -> str:
    """Format: RUN-YYYYMMDD-01 (2 digits)."""
    return f"RUN-{date_compact}-{seq:02d}"


def calculate_npi_checksum(nine_digits: str) -> int:
    """Compute the 10th check digit for a 9-digit NPI prefix using standard CMS Luhn with prefix 80840.

    Standard CMS Rule:
    1. Prepend '80840' to the 9-digit number.
    2. Starting from the rightmost digit of the 14-digit string, double every second digit.
    3. If doubling results in a 2-digit number, add the digits (or subtract 9).
    4. Sum all digits.
    5. Check digit = (10 - (sum % 10)) % 10.
    """
    full_prefix = "80840" + nine_digits
    total = 0
    # Process from right to left (rightmost position is doubled in 14-digit prefix before adding check digit)
    double = True
    for char in reversed(full_prefix):
        digit = int(char)
        if double:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
        double = not double

    check_digit = (10 - (total % 10)) % 10
    return check_digit


def generate_npi(seq: int, prefix_digit: int = 1) -> str:
    """Generate a valid 10-digit NPI from a deterministic sequence number.

    NPIs start with 1 or 2.
    """
    # 9-digit base: e.g. prefix_digit (1 digit) + 8-digit sequence
    base_9 = f"{prefix_digit}{seq:08d}"
    check = calculate_npi_checksum(base_9)
    return f"{base_9}{check}"


def validate_npi(npi: str) -> bool:
    """Validate that a string is a valid 10-digit NPI passing standard CMS Luhn checksum."""
    if not isinstance(npi, str) or not re.match(r"^\d{10}$", npi):
        return False
    nine_digits = npi[:9]
    expected_check = calculate_npi_checksum(nine_digits)
    actual_check = int(npi[9])
    return actual_check == expected_check

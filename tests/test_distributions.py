"""Unit tests for categorical distribution sampling and statistical convergence."""

from collections import Counter
import pytest
from generator.random_state import GeneratorRandomState
from generator.distributions import (
    sample_payer_type,
    sample_claim_status,
    sample_lines_count,
    sample_diagnoses_count,
)


def test_payer_distribution_convergence():
    rng = GeneratorRandomState(42)
    n = 3000
    samples = [sample_payer_type(rng) for _ in range(n)]
    counts = Counter(samples)

    comm_pct = counts["Commercial"] / n
    medicare_pct = counts["Medicare"] / n
    medicaid_pct = counts["Medicaid"] / n

    # Expected: 60% Comm, 25% Medicare, 15% Medicaid (+/- 4% tolerance at N=3000)
    assert 0.56 <= comm_pct <= 0.64
    assert 0.21 <= medicare_pct <= 0.29
    assert 0.11 <= medicaid_pct <= 0.19


def test_claim_status_distribution_convergence():
    rng = GeneratorRandomState(42)
    n = 5000
    samples = [sample_claim_status(rng) for _ in range(n)]
    counts = Counter(samples)

    paid_pct = counts["Paid"] / n
    part_pct = counts["Partially Paid"] / n
    den_pct = counts["Denied"] / n

    # Expected: Paid 75%, Partially Paid 15%, Denied 7% (+/- 3% tolerance at N=5000)
    assert 0.72 <= paid_pct <= 0.78
    assert 0.12 <= part_pct <= 0.18
    assert 0.05 <= den_pct <= 0.09


def test_lines_and_diagnoses_ranges():
    rng = GeneratorRandomState(42)
    for _ in range(500):
        lines = sample_lines_count(rng)
        assert 1 <= lines <= 5
        diags = sample_diagnoses_count(rng)
        assert 1 <= diags <= 3

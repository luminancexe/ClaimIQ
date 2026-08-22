"""Unit tests for deterministic seed reproducibility and generator pipeline consistency."""

import pytest
from generator.random_state import GeneratorRandomState
from generator.config import GeneratorConfig
from generator.generators.patients import generate_patients
from generator.generators.facilities import generate_facilities
from generator.generators.payers import generate_payers


def test_deterministic_seed_reproducibility():
    # Run 1 with Seed 42
    rng1 = GeneratorRandomState(42)
    pats1 = generate_patients(20, rng1)
    facs1 = generate_facilities(5, rng1)
    payers1 = generate_payers(5, rng1)

    # Run 2 with Seed 42
    rng2 = GeneratorRandomState(42)
    pats2 = generate_patients(20, rng2)
    facs2 = generate_facilities(5, rng2)
    payers2 = generate_payers(5, rng2)

    # Compare Run 1 and Run 2
    assert pats1 == pats2
    assert facs1 == facs2
    assert payers1 == payers2


def test_seed_divergence():
    # Run with Seed 42 vs Seed 99
    rng_a = GeneratorRandomState(42)
    pats_a = generate_patients(20, rng_a)

    rng_b = GeneratorRandomState(99)
    pats_b = generate_patients(20, rng_b)

    assert pats_a != pats_b
    assert [p["first_name"] for p in pats_a] != [p["first_name"] for p in pats_b]


def test_config_scale_profiles():
    cfg_small = GeneratorConfig(scale="small")
    assert cfg_small.profile.num_claims == 1000

    cfg_med = GeneratorConfig(scale="medium")
    assert cfg_med.profile.num_claims == 10000

    cfg_lrg = GeneratorConfig(scale="large")
    assert cfg_lrg.profile.num_claims == 100000

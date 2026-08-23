"""Unit tests for injection profiles configuration and targeting logic."""

import pytest
from generator.injector.profiles import PROFILES, get_profile


def test_all_standard_profiles_exist():
    assert "clean" in PROFILES
    assert "light" in PROFILES
    assert "moderate" in PROFILES
    assert "heavy" in PROFILES
    assert "targeted" in PROFILES


def test_clean_profile_zero_anomalies():
    p = get_profile("clean")
    assert p.target_rate == 0.0
    assert p.default_count_per_anomaly == 0
    assert len(p.get_effective_codes()) == 0


def test_profile_default_counts_ordering():
    light = get_profile("light")
    moderate = get_profile("moderate")
    heavy = get_profile("heavy")

    assert light.default_count_per_anomaly < moderate.default_count_per_anomaly
    assert moderate.default_count_per_anomaly < heavy.default_count_per_anomaly
    assert light.target_rate < moderate.target_rate < heavy.target_rate


def test_get_profile_case_insensitive():
    assert get_profile("MODERATE").name == "moderate"
    assert get_profile("  Heavy  ").name == "heavy"

    with pytest.raises(KeyError):
        get_profile("non_existent_profile")

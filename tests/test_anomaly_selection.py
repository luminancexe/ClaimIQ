"""Unit tests for anomaly taxonomy definitions, selection, and category resolution."""

import pytest
from generator.injector.models import SeverityLevel, AnomalyCategory
from generator.injector.taxonomy import (
    TAXONOMY,
    get_anomaly_definition,
    get_anomalies_by_category,
    list_all_anomalies,
)
from generator.injector.profiles import PROFILES, get_profile


def test_taxonomy_complete_inventory():
    # Exactly 67 anomaly codes E001 to E067
    assert len(TAXONOMY) == 67
    for i in range(1, 68):
        code = f"E{i:03d}"
        assert code in TAXONOMY, f"Missing expected anomaly code {code}"


def test_taxonomy_categories_representation():
    categories = {defn.category for defn in TAXONOMY.values()}
    assert len(categories) == 8
    assert AnomalyCategory.COMPLETENESS in categories
    assert AnomalyCategory.DUPLICATION in categories
    assert AnomalyCategory.REFERENTIAL in categories
    assert AnomalyCategory.FINANCIAL in categories
    assert AnomalyCategory.TEMPORAL in categories
    assert AnomalyCategory.LIFECYCLE in categories
    assert AnomalyCategory.BUSINESS_LOGIC in categories
    assert AnomalyCategory.FORMATTING in categories


def test_taxonomy_severities_validity():
    severities = {defn.severity for defn in TAXONOMY.values()}
    assert SeverityLevel.CRITICAL in severities
    assert SeverityLevel.HIGH in severities
    assert SeverityLevel.MEDIUM in severities
    assert SeverityLevel.LOW in severities


def test_taxonomy_lookup_helpers():
    defn_e023 = get_anomaly_definition("E023")
    assert defn_e023.code == "E023"
    assert defn_e023.category == AnomalyCategory.FINANCIAL
    assert defn_e023.severity == SeverityLevel.CRITICAL

    fin_anomalies = get_anomalies_by_category(AnomalyCategory.FINANCIAL)
    assert len(fin_anomalies) == 11  # E023 to E033

    all_anomalies = list_all_anomalies()
    assert len(all_anomalies) == 67
    assert all_anomalies[0].code == "E001"
    assert all_anomalies[-1].code == "E067"


def test_profile_code_resolution():
    clean_prof = get_profile("clean")
    assert len(clean_prof.get_effective_codes()) == 0

    mod_prof = get_profile("moderate")
    assert len(mod_prof.get_effective_codes()) == 67

    targeted_prof = get_profile("targeted")
    targeted_prof.enabled_codes = ["E001", "E023", "E034"]
    assert targeted_prof.get_effective_codes() == ["E001", "E023", "E034"]

"""Unit tests for duplication and uniqueness anomaly definitions."""

import pytest
from generator.injector.taxonomy import TAXONOMY


def test_duplication_anomaly_definitions():
    dup_codes = [f"E{i:03d}" for i in range(11, 16)]
    for code in dup_codes:
        defn = TAXONOMY[code]
        assert defn.category.value == "Duplication / Uniqueness"
        assert defn.severity.value in ("Critical", "High", "Medium")


def test_duplicate_reference_formatting():
    orig_claim_ref = "CLM-2025-0000100"
    dup_claim_ref = f"DUP-{orig_claim_ref}"
    assert dup_claim_ref.startswith("DUP-")
    assert orig_claim_ref in dup_claim_ref

    orig_enc_ref = "ENC-00000050"
    dup_enc_ref = f"DUP-{orig_enc_ref}"
    assert dup_enc_ref.startswith("DUP-")

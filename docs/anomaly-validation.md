# ClaimIQ — Phase 4 Anomaly Validation Suite

## 1. Validation Methodology & Principles

The Phase 4 Validation Suite (`generator/injector/validators.py`) ensures that:
1. **Intended Mutations Occurred**: Every entry in `anomaly_ground_truth` corresponds to an active, observable defect in the database.
2. **Clean Baseline Preservation**: Records not targeted for mutation remain intact.
3. **No Unintended Database Corruption**: No spontaneous referential integrity failures occur outside intentional cross-entity testing.
4. **Reversible Consistency**: Resetting anomalies returns the database to a state that passes 100% of Phase 3 clean baseline checks.

---

## 2. Validation Checks & Results

| Validation Check ID | Verification Target | Audit Logic | Status |
| :--- | :--- | :--- | :---: |
| **VAL-P4-001** | Ground Truth Completeness | Confirms every injected mutation has an active row in `anomaly_ground_truth`. | **PASS** |
| **VAL-P4-002** | Target Record Observation | Confirms `mutated_value` is live in MySQL on the target table and record ID. | **PASS** |
| **VAL-P4-003** | Inserted Clone Existence | Confirms duplicate records (`E011`–`E015`) exist with generated unique primary keys. | **PASS** |
| **VAL-P4-004** | Anomaly Count Accuracy | Confirms injected count matches requested profile (e.g. 201 for Moderate). | **PASS** |
| **VAL-P4-005** | Deterministic Reproducibility| Confirms identical seed reproduces exact same ground truth and mutation targets. | **PASS** |
| **VAL-P4-006** | Seed Divergence | Confirms different seeds select distinct mutation targets. | **PASS** |
| **VAL-P4-007** | Dry-Run Isolation | Confirms `--dry-run` makes zero database modifications and writes 0 ground truth rows. | **PASS** |
| **VAL-P4-008** | Two-Way Reversion | Confirms `--reset-anomalies` restores original values and purges duplicate rows. | **PASS** |
| **VAL-P4-009** | Phase 3 Baseline Compliance | Confirms post-reset database passes 100% of Phase 3 clean baseline audits. | **PASS** |

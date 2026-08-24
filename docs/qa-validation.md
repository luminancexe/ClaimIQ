# ClaimIQ — QA Engine Validation & Clean Baseline Audits

## 1. Clean Baseline Validation Philosophy

The QA Engine is verified against two complementary datasets:
1. **Clean Phase 3 Baseline**: Confirms that rules do not produce false alarms on valid, uncorrupted claims data.
2. **Phase 4 Injected Anomaly Dataset**: Confirms that rules successfully detect known-bad mutations across all 8 categories.

---

## 2. Validation Checkpoints & Results

| Checkpoint ID | Verification Objective | Target | Status |
| :--- | :--- | :--- | :---: |
| **VAL-QA-001** | Rule Registry Completeness | All 67 rules registered with valid dimensions and severities | **PASS** |
| **VAL-QA-002** | Clean Baseline Invariant Audit | Zero unexpected defects detected on clean Phase 3 data | **PASS** |
| **VAL-QA-003** | Financial Invariant Detection | Overpayments, variance, line sum mismatches flagged | **PASS** |
| **VAL-QA-004** | Temporal Sequence Detection | Out-of-order encounters, submissions, and payments flagged | **PASS** |
| **VAL-QA-005** | Lifecycle Conflict Detection | Denied/Rejected/Pending claims with disbursements flagged | **PASS** |
| **VAL-QA-006** | Code Validity & Luhn Check | Corrupted NPIs, malformed CPT, ICD-10, TINs flagged | **PASS** |
| **VAL-QA-007** | Ground Truth Matching Accuracy | Compound key matching (anomaly + table + ID) verified | **PASS** |
| **VAL-QA-008** | DQ Scoring Determinism | Identical input produces identical weighted DQ scores | **PASS** |
| **VAL-QA-009** | Dry-Run Isolation | Simulated runs make zero writes to MySQL QA tables | **PASS** |

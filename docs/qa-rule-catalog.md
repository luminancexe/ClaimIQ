# ClaimIQ — QA Rule Catalog (R-E001 to R-E067)

## 1. QA Rule Inventory Overview

The ClaimIQ Phase 5 QA Rule Catalog defines **67 deterministic detection rules** mapped directly to the Phase 4 Anomaly Taxonomy (`E001`–`E067`). Every rule specifies its DQ dimension, category, default severity, target schema entity, and detection strategy.

---

## 2. Dimension 1: Completeness (Weight: 15%)

| Rule Code | Rule Name | Severity | Target Table | Target Column | Mapped Anomaly | Detection Method |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **R-E001** | Mandatory Patient State Completeness | Low | `patients` | `address_state` | `E001` | SQL_SET |
| **R-E002** | Provider Facility Assignment Completeness | Medium | `providers` | `facility_id` | `E002` | SQL_SET |
| **R-E003** | Coverage Policy Group Completeness | Low | `patient_coverage`| `group_number` | `E003` | SQL_SET |
| **R-E004** | Claim Line Procedure Description Completeness| Low | `claim_lines` | `procedure_description`| `E004` | SQL_SET |
| **R-E005** | Inpatient Discharge Timestamp Completeness | Medium | `encounters` | `discharge_date` | `E005` | SQL_SET |
| **R-E006** | Adjudicated Claim Adjudication Date | High | `claims` | `adjudication_date` | `E006` | SQL_SET |
| **R-E007** | Adjustment Narrative Description | Low | `adjustments` | `adjustment_description`| `E007` | SQL_SET |
| **R-E008** | Claim Status Transition Reason Completeness| Low | `claim_status_history`| `transition_reason`| `E008` | SQL_SET |
| **R-E009** | Terminated Policy End Date Completeness | Low | `patient_coverage`| `termination_date` | `E009` | SQL_SET |
| **R-E010** | Encounter Diagnosis Description Completeness| Medium | `encounter_diagnoses`| `diagnosis_description`| `E010` | SQL_SET |

---

## 3. Dimension 2: Uniqueness (Weight: 10%)

| Rule Code | Rule Name | Severity | Target Table | Target Column | Mapped Anomaly | Detection Method |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **R-E011** | Duplicate Claim Header Detection | High | `claims` | `claim_reference` | `E011` | SQL_SET |
| **R-E012** | Duplicate Claim Line Item Detection | High | `claim_lines` | `cpt_code` | `E012` | SQL_SET |
| **R-E013** | Duplicate Payment Transaction Detection | High | `payments` | `paid_amount` | `E013` | SQL_SET |
| **R-E014** | Duplicate Remittance Trace Number Detection | Medium | `remittances` | `check_trace_number` | `E014` | SQL_SET |
| **R-E015** | Duplicate Clinical Encounter Detection | High | `encounters` | `encounter_reference` | `E015` | SQL_SET |

---

## 4. Dimension 3: Referential Integrity (Weight: 20%)

| Rule Code | Rule Name | Severity | Target Table | Target Column | Mapped Anomaly | Detection Method |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **R-E016** | Provider Facility State Alignment | Medium | `providers` | `facility_id` | `E016` | SQL_SET |
| **R-E017** | Claim Payer and Policy Plan Alignment | High | `claims` | `payer_id` | `E017` | SQL_SET |
| **R-E018** | Inpatient Hospital Provider Specialty | Medium | `encounters` | `provider_id` | `E018` | SQL_SET |
| **R-E019** | Claim Submission Active Policy Check | High | `claims` | `payer_id` | `E019` | SQL_SET |
| **R-E020** | Claim Line Cross-Claim Integrity | High | `claim_lines` | `claim_id` | `E020` | SQL_SET |
| **R-E021** | Payment Remittance and Claim Payer Match| High | `payments` | `claim_id` | `E021` | SQL_SET |
| **R-E022** | Remittance Batch Payer Alignment | High | `remittances` | `payer_id` | `E022` | SQL_SET |

---

## 5. Dimension 4: Financial Integrity (Weight: 20%)

| Rule Code | Rule Name | Severity | Target Table | Target Column | Mapped Anomaly | Detection Method |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **R-E023** | Payment Exceeds Total Billed (Overpayment) | Critical | `payments` | `paid_amount` | `E023` | SQL_SET |
| **R-E024** | Adjustment Exceeds Total Billed Charge | High | `adjustments` | `adjustment_amount` | `E024` | SQL_SET |
| **R-E025** | Inflated Contractual Write-off Ratio | High | `adjustments` | `adjustment_amount` | `E025` | SQL_SET |
| **R-E026** | Reconciliation Patient Resp Ledger Discrepancy | Medium | `reconciliations` | `total_patient_resp` | `E026` | SQL_SET |
| **R-E027** | Remittance Header vs Payment Sum Mismatch| Critical | `remittances` | `total_paid_amount` | `E027` | SQL_SET |
| **R-E028** | Cumulative Claim Overdisbursement | Critical | `payments` | `paid_amount` | `E028` | SQL_SET |
| **R-E029** | Reconciliation Ledger Non-Zero Variance | Critical | `reconciliations` | `variance_amount` | `E029` | SQL_SET |
| **R-E030** | Claim Header Billed vs Line Sum Mismatch | Critical | `claims` | `total_billed_amount`| `E030` | SQL_SET |
| **R-E031** | Claim Line Item Arithmetic Mismatch | High | `claim_lines` | `line_billed_amount` | `E031` | SQL_SET |
| **R-E032** | Zero-Billed Claim with Positive Payment | High | `claims` | `total_billed_amount`| `E032` | SQL_SET |
| **R-E033** | Paid Claim Missing Payment Disbursement | High | `payments` | `paid_amount` | `E033` | SQL_SET |

---

## 6. Dimension 5: Temporal Consistency (Weight: 10%)

| Rule Code | Rule Name | Severity | Target Table | Target Column | Mapped Anomaly | Detection Method |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **R-E034** | Clinical DOS Precedes Claim Submission | High | `encounters` | `date_of_service` | `E034` | SQL_SET |
| **R-E035** | Claim Submission Precedes Adjudication | High | `claims` | `submission_date` | `E035` | SQL_SET |
| **R-E036** | Payment Date Succeeds Claim Submission | High | `payments` | `payment_date` | `E036` | SQL_SET |
| **R-E037** | Payment Date Succeeds Adjudication Decision| High | `payments` | `payment_date` | `E037` | SQL_SET |
| **R-E038** | Remittance Generation Succeeds Adjudication| Medium | `remittances` | `remittance_date` | `E038` | SQL_SET |
| **R-E039** | Denial Notice Succeeds Claim Submission | High | `denials` | `denial_date` | `E039` | SQL_SET |
| **R-E040** | Inpatient Discharge Succeeds Admission Date| High | `encounters` | `discharge_date` | `E040` | SQL_SET |
| **R-E041** | Future-Dated Claim Submission Event | High | `claims` | `submission_date` | `E041` | SQL_SET |
| **R-E042** | Claim Submission Succeeds Patient DOB | Critical | `claims` | `submission_date` | `E042` | SQL_SET |

---

## 7. Dimension 6: Accuracy & State Logic (Weight: 10%)

| Rule Code | Rule Name | Severity | Target Table | Target Column | Mapped Anomaly | Detection Method |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **R-E043** | Illegal Direct Transition (Denied to Paid)| High | `claim_status_history`| `previous_status_code`| `E043` | SQL_SET |
| **R-E044** | Paid Claim Zero Paid Ledger Inconsistency | High | `reconciliations` | `total_paid` | `E044` | SQL_SET |
| **R-E045** | Denied Claim with Payment Disbursements | High | `claims` | `current_status_code`| `E045` | SQL_SET |
| **R-E046** | Rejected Claim with Payment Disbursements | High | `claims` | `current_status_code`| `E046` | SQL_SET |
| **R-E047** | Pending Review Claim with Finalized Payment| Medium | `claims` | `current_status_code`| `E047` | SQL_SET |
| **R-E048** | Unadjudicated Claim Flagged as Reconciled | Medium | `claims` | `is_reconciled` | `E048` | SQL_SET |
| **R-E049** | Finalized Paid Claim Missing Adjudication Date| Medium | `claims` | `adjudication_date` | `E049` | SQL_SET |
| **R-E050** | Redundant Consecutive Terminal State Transition| Low | `claim_status_history`| `new_status_code` | `E050` | SQL_SET |
| **R-E051** | Positive-Billed Claim Header Lacks Lines | High | `claims` | `claim_id` | `E051` | SQL_SET |
| **R-E052** | Claim Patient Discordant with Encounter | Critical | `claims` | `patient_id` | `E052` | SQL_SET |
| **R-E053** | Claim Billing Provider Discordant with Encounter| Medium | `claims` | `billing_provider_id`| `E053` | SQL_SET |
| **R-E054** | Claim Submitted Outside Timely Filing Limit | High | `claims` | `submission_date` | `E054` | SQL_SET |
| **R-E055** | Payment Allocated to Submitted Claim | High | `claims` | `current_status_code`| `E055` | SQL_SET |
| **R-E056** | Contradictory Denial Record on Paid Claim | High | `denials` | `claim_id` | `E056` | SQL_SET |
| **R-E057** | Reconciliation Balanced Despite Variance | Critical | `reconciliations` | `reconciliation_status`| `E057` | SQL_SET |
| **R-E058** | Reconciliation Unbalanced with Zero Variance| Medium | `reconciliations` | `reconciliation_status`| `E058` | SQL_SET |
| **R-E059** | Clinical DOS Outside Active Coverage Window| High | `patient_coverage`| `effective_date` | `E059` | SQL_SET |
| **R-E060** | Inpatient Hospitalization Outpatient CPT Conflict| Low | `claim_lines` | `cpt_code` | `E060` | SQL_SET |

---

## 8. Dimension 7: Validity & Conformance (Weight: 15%)

| Rule Code | Rule Name | Severity | Target Table | Target Column | Mapped Anomaly | Detection Method |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **R-E061** | Provider NPI Checksum Algorithm Validation| High | `providers` | `npi` | `E061` | **PYTHON_VALIDATION** (CMS Luhn) |
| **R-E062** | CPT / HCPCS Procedure Code Syntax Conformance| Medium | `claim_lines` | `cpt_code` | `E062` | SQL_SET |
| **R-E063** | ICD-10-CM Clinical Diagnosis Syntax Conformance| Medium | `encounter_diagnoses`| `icd10_code` | `E063` | SQL_SET |
| **R-E064** | NUCC Provider Specialty Taxonomy Code Conformance| Low | `providers` | `taxonomy_code` | `E064` | SQL_SET |
| **R-E065** | Claim Business Reference Format Conformance| Low | `claims` | `claim_reference` | `E065` | SQL_SET |
| **R-E066** | CARC Adjustment Reason Code Conformance | Low | `adjustments` | `reason_code` | `E066` | SQL_SET |
| **R-E067** | Facility Federal Taxpayer ID (TIN) Conformance| Low | `facilities` | `tin` | `E067` | SQL_SET |

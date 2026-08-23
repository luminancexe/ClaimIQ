# ClaimIQ — Anomaly Taxonomy Registry (E001–E067)

## 1. Overview & Anomaly Classification

The ClaimIQ Anomaly Taxonomy classifies **67 distinct defect types** across 8 operational categories. Every anomaly is mapped to an authoritative code (`E001`–`E067`), severity level, target schema entity, mutation strategy, and expected business invariant violation.

---

## 2. Category 1: Completeness / Missing Mandatory Fields (E001–E010)

| Code | Anomaly Name | Severity | Target Table | Target Column | Expected Violation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **E001** | Missing Patient Demographic Field | Low | `patients` | `address_state` | Mandatory patient geographic state is missing / blank |
| **E002** | Missing Provider Facility Link | Medium | `providers` | `facility_id` | Facility-based clinician missing healthcare facility link |
| **E003** | Missing Policy Group Number | Low | `patient_coverage`| `group_number` | Commercial insurance coverage missing policy group identifier |
| **E004** | Missing Procedure Description | Low | `claim_lines` | `procedure_description` | Itemized service line missing narrative procedure description |
| **E005** | Missing Inpatient Discharge Date | Medium | `encounters` | `discharge_date` | Inpatient hospital encounter missing discharge timestamp |
| **E006** | Missing Claim Adjudication Date | High | `claims` | `adjudication_date` | Finalized adjudicated claim missing adjudication timestamp |
| **E007** | Missing Adjustment Description | Low | `adjustments` | `adjustment_description` | Financial adjustment missing explanatory text |
| **E008** | Missing Status Transition Reason | Low | `claim_status_history`| `transition_reason` | Audit history missing status change reason |
| **E009** | Missing Coverage Termination Date | Low | `patient_coverage`| `termination_date` | Terminated secondary policy missing termination date |
| **E010** | Missing Diagnosis Description | Medium | `encounter_diagnoses`| `diagnosis_description`| Secondary ICD-10 record missing narrative description |

---

## 3. Category 2: Duplication & Uniqueness (E011–E015)

| Code | Anomaly Name | Severity | Target Table | Target Column | Expected Violation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **E011** | Duplicate Claim Header | High | `claims` | `claim_reference` | Potential duplicate billing on identical patient, provider, and DOS |
| **E012** | Duplicate Claim Line | High | `claim_lines` | `cpt_code` | Duplicate service line billed within a single claim |
| **E013** | Duplicate Payment Transaction | High | `payments` | `paid_amount` | Duplicate payment disbursement on single claim |
| **E014** | Duplicate Remittance Trace Number | Medium | `remittances` | `check_trace_number` | Duplicate check trace number across remittances |
| **E015** | Duplicate Clinical Encounter | High | `encounters` | `encounter_reference` | Duplicate clinical encounter for same patient on same date |

---

## 4. Category 3: Referential Integrity & Cross-Entity Mismatches (E016–E022)

| Code | Anomaly Name | Severity | Target Table | Target Column | Expected Violation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **E016** | Provider Facility State Mismatch | Medium | `providers` | `facility_id` | Provider practicing at facility in non-licensed state |
| **E017** | Payer Insurance Plan Mismatch | High | `claims` | `payer_id` | Claim billed to payer discordant with patient insurance plan |
| **E018** | Provider Specialty Mismatch | Medium | `encounters` | `provider_id` | Rendering clinician specialty incompatible with encounter setting |
| **E019** | Patient Policy Payer Mismatch | High | `claims` | `payer_id` | Claim submitted to payer where patient has no active policy |
| **E020** | Claim Line Cross-Claim Linkage | High | `claim_lines` | `claim_id` | Claim line belongs to discordant parent claim context |
| **E021** | Payment Allocated to Discordant Claim| High | `payments` | `claim_id` | Payment allocated to claim belonging to a different payer |
| **E022** | Remittance Payer Mismatch | High | `remittances` | `payer_id` | Remittance paying entity does not match claim payer |

---

## 5. Category 4: Financial & Reconciliation Defects (E023–E033)

| Code | Anomaly Name | Severity | Target Table | Target Column | Expected Violation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **E023** | Payment Exceeds Billed Amount | Critical | `payments` | `paid_amount` | Overpayment anomaly: Paid > Billed |
| **E024** | Adjustment Exceeds Balance | High | `adjustments` | `adjustment_amount` | Total adjustments exceed unadjudicated claim balance |
| **E025** | Inflated Contractual Adjustment | High | `adjustments` | `adjustment_amount` | Contractual write-off exceeds allowable fee schedule |
| **E026** | Incorrect Patient Responsibility | Medium | `reconciliations` | `total_patient_resp` | Copay/coinsurance out of balance with adjustments |
| **E027** | Remittance Batch Total Mismatch | Critical | `remittances` | `total_paid_amount` | Remittance header total does not equal sum of payments |
| **E028** | Duplicate Payment Overdisbursement | Critical | `payments` | `paid_amount` | Cumulative payments exceed total billed amount |
| **E029** | Reconciliation Ledger Variance | Critical | `reconciliations` | `variance_amount` | Reconciliation ledger fails zero-variance invariant |
| **E030** | Header Billed vs Line Sum Mismatch | Critical | `claims` | `total_billed_amount`| Claim header billed amount does not equal sum of lines |
| **E031** | Line Billed Arithmetic Mismatch | High | `claim_lines` | `line_billed_amount` | Claim line calculation error: line_billed != units * price |
| **E032** | Zero-Billed Claim with Payment | High | `claims` | `total_billed_amount`| Zero-dollar billed claim received positive payment |
| **E033** | Paid Claim with Zero Payment | High | `payments` | `paid_amount` | Paid claim has no positive cash payment transaction |

---

## 6. Category 5: Temporal & Chronological Anomalies (E034–E042)

| Code | Anomaly Name | Severity | Target Table | Target Column | Expected Violation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **E034** | Date of Service After Submission | High | `encounters` | `date_of_service` | Chronological violation: DOS > Submission date |
| **E035** | Submission After Adjudication | High | `claims` | `submission_date` | Chronological violation: Submission > Adjudication date |
| **E036** | Payment Date Before Submission | High | `payments` | `payment_date` | Chronological violation: Payment date < Submission date |
| **E037** | Payment Date Before Adjudication | High | `payments` | `payment_date` | Chronological violation: Payment date < Adjudication date |
| **E038** | Remittance Date Before Adjudication | Medium | `remittances` | `remittance_date` | Chronological violation: Remittance date < Adjudication date |
| **E039** | Denial Date Before Submission | High | `denials` | `denial_date` | Chronological violation: Denial date < Submission date |
| **E040** | Discharge Before Date of Service | High | `encounters` | `discharge_date` | Chronological violation: Discharge date < Date of service |
| **E041** | Future-Dated Claim Event | High | `claims` | `submission_date` | Chronological violation: Event timestamp in the future |
| **E042** | Claim Submission Precedes DOB | Critical | `claims` | `submission_date` | Chronological violation: Submission precedes patient DOB |

---

## 7. Category 6: Claim Lifecycle & State Machine Anomalies (E043–E050)

| Code | Anomaly Name | Severity | Target Table | Target Column | Expected Violation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **E043** | Invalid Direct State Transition | High | `claim_status_history`| `previous_status_code`| Illegal FSM transition bypassing mandatory workflow stages |
| **E044** | Paid Claim with Zero Paid Balance | High | `reconciliations` | `total_paid` | Claim status is Paid but total paid financial amount is 0.00 |
| **E045** | Denied Claim with Positive Payment| High | `claims` | `current_status_code`| Claim marked Denied despite positive cash disbursement |
| **E046** | Rejected Claim with Payment | High | `claims` | `current_status_code`| Claim in front-end Rejected state contains payments |
| **E047** | Pending Claim with Finalized Payment| Medium | `claims` | `current_status_code`| In-flight Pending claim contains premature payment |
| **E048** | Submitted Claim Marked Reconciled | Medium | `claims` | `is_reconciled` | Unadjudicated claim prematurely flagged as reconciled |
| **E049** | Paid Claim Missing Adjudication Date| Medium | `claims` | `adjudication_date` | Terminal adjudicated claim missing adjudication timestamp |
| **E050** | Duplicate Final Status Transitions | Low | `claim_status_history`| `new_status_code` | Redundant duplicate state transition in claim history |

---

## 8. Category 7: Business Logic & Operational Inconsistencies (E051–E060)

| Code | Anomaly Name | Severity | Target Table | Target Column | Expected Violation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **E051** | Claim Without Service Lines | High | `claim_lines` | `claim_id` | Billed claim header exists without any itemized lines |
| **E052** | Claim Patient Mismatch with Encounter| Critical | `claims` | `patient_id` | Discordant patient linkage between claim and encounter |
| **E053** | Claim Provider Mismatch | Medium | `claims` | `billing_provider_id`| Claim billing provider mismatch with encounter clinician |
| **E054** | Submission Outside Timely Filing | High | `claims` | `submission_date` | Claim submission exceeds payer statutory timely-filing window |
| **E055** | Payment for In-Flight Claim | High | `claims` | `current_status_code`| Cash disbursement recorded against active unadjudicated claim |
| **E056** | Denial Record on Paid Claim | High | `denials` | `claim_id` | Contradictory denial attached to fully paid claim |
| **E057** | Balanced Status with Variance | Critical | `reconciliations` | `reconciliation_status`| Status flagged BALANCED despite non-zero variance |
| **E058** | Unbalanced Status with Zero Variance| Medium | `reconciliations` | `reconciliation_status`| Status flagged UNBALANCED despite zero variance |
| **E059** | Service Date Outside Coverage | High | `patient_coverage`| `effective_date` | Patient lacked active policy coverage on date of service |
| **E060** | Inpatient Encounter Outpatient Codes| Low | `claim_lines` | `cpt_code` | Procedural coding discordant with inpatient encounter type |

---

## 9. Category 8: Code & Formatting Anomalies (E061–E067)

| Code | Anomaly Name | Severity | Target Table | Target Column | Expected Violation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **E061** | Invalid Provider NPI Checksum | High | `providers` | `npi` | Provider 10-digit NPI fails standard CMS Luhn checksum |
| **E062** | Malformed CPT Procedure Code | Medium | `claim_lines` | `cpt_code` | Malformed non-standard CPT procedure code format |
| **E063** | Malformed ICD-10 Diagnosis Code | Medium | `encounter_diagnoses`| `icd10_code` | Malformed non-standard ICD-10-CM diagnostic code |
| **E064** | Malformed NUCC Taxonomy Code | Low | `providers` | `taxonomy_code` | Malformed provider NUCC specialty taxonomy code |
| **E065** | Malformed Business Reference | Low | `claims` | `claim_reference` | Claim reference violates enterprise format standard |
| **E066** | Invalid Adjustment Reason Code | Low | `adjustments` | `reason_code` | Non-standard CARC adjustment reason code |
| **E067** | Malformed Facility Tax ID (TIN) | Low | `facilities` | `tin` | Malformed Federal Taxpayer Identification Number format |

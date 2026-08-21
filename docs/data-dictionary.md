# ClaimIQ — Comprehensive Data Dictionary (MySQL 8.x)

This document provides the complete, authoritative data dictionary for all 22 tables and columns in the ClaimIQ MySQL 8.x relational schema.

---

## Index of Database Tables

| Table Name | Domain | Primary Purpose | Row Cardinality Profile |
| :--- | :--- | :--- | :--- |
| `ref_claim_statuses` | Reference | Controlled claim lifecycle states | Static (7 rows) |
| `ref_issue_statuses` | Reference | Controlled operational issue lifecycle states | Static (7 rows) |
| `ref_severities` | Reference | 4-tier QA severity triage levels & SLAs | Static (4 rows) |
| `ref_dq_dimensions` | Reference | 7 healthcare data quality dimensions | Static (7 rows) |
| `ref_root_causes` | Reference | Standardized root-cause taxonomy codes | Static (7 rows) |
| `ref_adjustment_group_codes`| Reference | Standard CARC/RARC adjustment group codes | Static (5 rows) |
| `patients` | Master | Synthetic patient demographics & references | Medium (~10,000+) |
| `facilities` | Master | Synthetic clinics, hospitals & facilities | Low (~100+) |
| `providers` | Master | Synthetic clinicians & National Provider Identifiers | Low-Med (~1,000+) |
| `payers` | Master | Commercial & government insurance payers | Low (~50) |
| `insurance_plans` | Master | Specific insurance plan products & benefit tiers | Low-Med (~200) |
| `patient_coverage` | Clinical/Admin | Patient enrollment & policy memberships | Medium (~15,000+) |
| `encounters` | Clinical | Clinical care episodes between patient & provider | High (~50,000+) |
| `encounter_diagnoses` | Clinical | Primary and secondary ICD-10 diagnostic codes | High (~100,000+) |
| `claims` | Claims | Standard billing claim headers (837 equivalent) | High (~100,000+) |
| `claim_lines` | Claims | Itemized procedural service lines (CPT/HCPCS) | Very High (~300,000+) |
| `claim_status_history` | Claims | State transition audit log for claims | Very High (~250,000+) |
| `remittances` | Financial | Electronic Remittance Advice (ERA 835 batches) | High (~40,000+) |
| `payments` | Financial | Disbursed payment allocations per claim | High (~80,000+) |
| `adjustments` | Financial | Contractual write-offs & patient cost-sharing | High (~90,000+) |
| `denials` | Financial | Formally denied claim line items & CARC codes | Med-High (~15,000+) |
| `reconciliations` | Financial | Mathematical reconciliation balance records | High (~100,000+) |
| `qa_rule_categories` | QA Metadata | Functional categories of validation rules | Static (~10 rows) |
| `qa_rules` | QA Metadata | Definitions of active SQL QA validation rules | Low (~50 rows) |
| `qa_execution_runs` | QA Metadata | Execution run history, batch metrics & DQ score | Med (~1,000+) |
| `qa_results` | QA Metadata | Telemetry & detection counts per rule per run | High (~50,000+) |
| `issues` | Operations | Operational discrepancy records flagged by QA | High (~20,000+) |
| `issue_history` | Operations | State transition history & assignment changes | High (~50,000+) |
| `issue_notes` | Operations | Analyst investigation findings & root-cause notes | High (~40,000+) |
| `audit_events` | Governance | Immutable application audit log (tamper-evident) | Very High (~500,000+) |

---

## Detailed Table & Column Specifications

### 1. Reference Domain Tables

#### `ref_claim_statuses`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description & Allowed Values |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `status_code` | `VARCHAR(32)` | No | None | `PRIMARY KEY` | Unique status code (`Submitted`, `Accepted`, `Rejected`, `Pending`, `Denied`, `Paid`, `Partially Paid`). |
| `status_name` | `VARCHAR(64)` | No | None | None | Human-readable status title. |
| `description` | `VARCHAR(255)` | No | None | None | Detailed operational definition of the state. |
| `is_terminal` | `BOOLEAN` | No | `0` | None | Flag indicating if state is an adjudicated/closed terminal state. |

#### `ref_issue_statuses`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description & Allowed Values |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `status_code` | `VARCHAR(32)` | No | None | `PRIMARY KEY` | Unique status code (`Detected`, `Open`, `Investigating`, `Resolved`, `False Positive`, `Escalated`, `Ignored`). |
| `status_name` | `VARCHAR(64)` | No | None | None | Display title for analyst workbenches. |
| `description` | `VARCHAR(255)` | No | None | None | Operational role & entry/exit definition. |
| `is_terminal` | `BOOLEAN` | No | `0` | None | Flag indicating if the issue is closed. |

#### `ref_severities`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description & Allowed Values |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `severity_code` | `VARCHAR(16)` | No | None | `PRIMARY KEY` | Code (`Critical`, `High`, `Medium`, `Low`). |
| `severity_name` | `VARCHAR(32)` | No | None | None | Display title. |
| `sla_hours` | `INT UNSIGNED` | No | `24` | None | Target SLA turnaround time in hours (4, 24, 72, 168). |
| `priority_rank` | `TINYINT UNSIGNED` | No | `1` | None | Numerical priority for sorting (1=Critical, 4=Low). |

#### `ref_dq_dimensions`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description & Allowed Values |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `dimension_code` | `VARCHAR(32)` | No | None | `PRIMARY KEY` | Code (`Accuracy`, `Completeness`, `Consistency`, `Validity`, `Uniqueness`, `Timeliness`, `Referential Integrity`). |
| `dimension_name` | `VARCHAR(64)` | No | None | None | Name of the dimension. |
| `weight` | `DECIMAL(4, 2)`| No | `0.10` | `CHECK (weight >= 0 AND weight <= 1)` | Weight used in composite DQ Score formula ($\sum = 1.00$). |
| `description` | `VARCHAR(255)` | No | None | None | Scope definition in healthcare context. |

#### `ref_root_causes`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description & Allowed Values |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `root_cause_code` | `VARCHAR(64)` | No | None | `PRIMARY KEY` | Code (`DATA_ENTRY_ERROR`, `SYSTEM_CONFIG_ERROR`, `PAYER_ADJUDICATION_DEFECT`, `TIMING_DESYNCHRONIZATION`, `DUPLICATE_SUBMISSION`, `REFERENTIAL_MISSING_MASTER`, `CALCULATION_ROUNDING_DEFECT`). |
| `root_cause_name` | `VARCHAR(100)` | No | None | None | Standard root-cause title. |
| `description` | `VARCHAR(255)` | No | None | None | Rationale for classification. |

#### `ref_adjustment_group_codes`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description & Allowed Values |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `group_code` | `VARCHAR(8)` | No | None | `PRIMARY KEY` | Standard CARC group code (`CO`, `PR`, `OA`, `PI`, `CR`). |
| `group_name` | `VARCHAR(64)` | No | None | None | Group title (e.g., Contractual Obligation, Patient Responsibility). |
| `description` | `VARCHAR(255)` | No | None | None | Explanation of financial allocation. |

---

### 2. Patient & Provider Domain Tables

#### `patients`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `patient_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `patient_reference` | `VARCHAR(64)` | No | None | `UNIQUE KEY uq_patients_ref` | Business identifier (e.g., `PAT-00008421`). |
| `first_name` | `VARCHAR(100)` | No | None | None | Synthetic first name. |
| `last_name` | `VARCHAR(100)` | No | None | None | Synthetic last name. |
| `date_of_birth` | `DATE` | No | None | None | Synthetic birth date. |
| `gender` | `VARCHAR(16)` | No | None | None | Gender identity (`MALE`, `FEMALE`, `OTHER`). |
| `address_state` | `VARCHAR(2)` | No | None | None | Two-letter US state code (e.g., `CA`, `TX`). |
| `created_at` | `DATETIME(6)` | No | `CURRENT_TIMESTAMP(6)` | None | Ingestion timestamp (UTC). |

#### `facilities`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `facility_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `facility_reference`| `VARCHAR(64)` | No | None | `UNIQUE KEY uq_facilities_ref`| Business identifier (e.g., `FAC-001`). |
| `facility_name` | `VARCHAR(150)` | No | None | None | Clinic or hospital facility name. |
| `tin` | `VARCHAR(10)` | No | None | None | Tax Identification Number (9 digits). |
| `facility_type` | `VARCHAR(50)` | No | None | None | Type (`Inpatient Hospital`, `Outpatient Clinic`, etc.). |
| `state` | `VARCHAR(2)` | No | None | None | Facility state location. |

#### `providers`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `provider_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `provider_reference`| `VARCHAR(64)` | No | None | `UNIQUE KEY uq_providers_ref` | Business identifier (e.g., `PRV-0012`). |
| `facility_id` | `BIGINT UNSIGNED` | Yes | `NULL` | `FOREIGN KEY fk_providers_facilities` | Primary practice facility. |
| `first_name` | `VARCHAR(100)` | No | None | None | Clinician first name. |
| `last_name` | `VARCHAR(100)` | No | None | None | Clinician last name. |
| `npi` | `VARCHAR(10)` | No | None | `UNIQUE KEY uq_providers_npi` | 10-digit National Provider Identifier. |
| `taxonomy_code` | `VARCHAR(10)` | No | None | None | 10-character healthcare provider taxonomy code. |
| `specialty` | `VARCHAR(100)` | No | None | None | Medical specialty (e.g., `Internal Medicine`). |

#### `payers`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `payer_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `payer_reference` | `VARCHAR(64)` | No | None | `UNIQUE KEY uq_payers_ref` | Business identifier (e.g., `PAY-001`). |
| `payer_name` | `VARCHAR(150)` | No | None | None | Payer organization title. |
| `payer_type` | `VARCHAR(50)` | No | None | None | Category (`Commercial`, `Medicare`, `Medicaid`). |
| `timely_filing_days`| `INT UNSIGNED` | No | `365` | None | Filing deadline in days from service date. |

#### `insurance_plans`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `plan_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `payer_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_plans_payers` | Sponsoring payer organization. |
| `plan_name` | `VARCHAR(150)` | No | None | None | Benefit plan title. |
| `plan_type` | `VARCHAR(50)` | No | None | None | Benefit model (`HMO`, `PPO`, `EPO`, `POS`). |

#### `patient_coverage`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `coverage_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `patient_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_cov_patients` | Covered patient. |
| `plan_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_cov_plans` | Enrolled insurance plan. |
| `member_id` | `VARCHAR(64)` | No | None | None | Policy member ID. |
| `group_number` | `VARCHAR(64)` | Yes | `NULL` | None | Employer group identifier. |
| `effective_date` | `DATE` | No | None | None | Coverage policy start date. |
| `termination_date`| `DATE` | Yes | `NULL` | None | Coverage expiration date. |
| `is_primary` | `BOOLEAN` | No | `1` | None | Flag indicating primary vs secondary insurance. |

---

### 3. Clinical & Encounter Domain Tables

#### `encounters`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `encounter_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `encounter_reference`| `VARCHAR(64)` | No | None | `UNIQUE KEY uq_encounters_ref`| Business identifier (e.g., `ENC-0001`). |
| `patient_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_enc_patients` | Treated patient. |
| `provider_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_enc_providers` | Rendering clinician. |
| `facility_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_enc_facilities`| Service facility location. |
| `date_of_service` | `DATE` | No | None | None | Date medical care was delivered. |
| `encounter_type` | `VARCHAR(50)` | No | None | None | Type (`Inpatient`, `Outpatient`, `Emergency`, `Telehealth`). |
| `discharge_date` | `DATE` | Yes | `NULL` | None | Discharge date for inpatient stays. |

#### `encounter_diagnoses`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `diagnosis_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `encounter_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_diag_encounters`| Parent clinical encounter. |
| `icd10_code` | `VARCHAR(16)` | No | None | None | Alphanumeric ICD-10-CM diagnosis code. |
| `diagnosis_description`| `VARCHAR(255)`| Yes | `NULL` | None | Text description of diagnosis. |
| `is_primary` | `BOOLEAN` | No | `0` | None | Flag indicating primary admitting diagnosis. |
| `sequence_number` | `INT UNSIGNED` | No | `1` | None | Order of coding on claim. |

---

### 4. Claims Domain Tables

#### `claims`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `claim_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `claim_reference` | `VARCHAR(64)` | No | None | `UNIQUE KEY uq_claims_ref` | Business identifier (e.g., `CLM-2026-0001`). |
| `encounter_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_claims_encounters` | Originating clinical encounter. |
| `patient_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_claims_patients` | Treated patient. |
| `billing_provider_id`| `BIGINT UNSIGNED`| No | None | `FOREIGN KEY fk_claims_providers` | Billing clinician/group. |
| `payer_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_claims_payers` | Target payer organization. |
| `current_status_code`| `VARCHAR(32)` | No | `'Submitted'` | `FOREIGN KEY fk_claims_status` | Current lifecycle state. |
| `total_billed_amount`| `DECIMAL(12, 2)`| No | `0.00` | `CHECK (total_billed_amount >= 0.00)` | Total gross charges billed on claim. |
| `submission_date` | `DATE` | No | None | None | Electronic transmission date. |
| `adjudication_date`| `DATE` | Yes | `NULL` | None | Date finalized by payer. |
| `is_reconciled` | `BOOLEAN` | No | `0` | None | Flag indicating balanced accounting closure. |

#### `claim_lines`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `claim_line_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `claim_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_lines_claims` | Parent claim header. |
| `line_number` | `INT UNSIGNED` | No | `1` | None | Sequential line number on claim. |
| `cpt_code` | `VARCHAR(16)` | No | None | None | 5-digit CPT or HCPCS procedural code. |
| `procedure_description`| `VARCHAR(255)`| Yes | `NULL` | None | Description of medical service. |
| `units` | `DECIMAL(8, 2)` | No | `1.00` | `CHECK (units > 0.00)` | Service units rendered. |
| `unit_price` | `DECIMAL(12, 2)`| No | `0.00` | `CHECK (unit_price >= 0.00)` | Charge per unit. |
| `line_billed_amount` | `DECIMAL(12, 2)`| No | `0.00` | `CHECK (line_billed_amount >= 0.00)` | Total billed for line ($\text{units} \times \text{unit\_price}$). |
| `line_status` | `VARCHAR(32)` | No | `'Submitted'` | None | Status of individual line item. |

#### `claim_status_history`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `history_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `claim_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_csh_claims` | Target claim. |
| `previous_status_code`| `VARCHAR(32)` | Yes | `NULL` | `FOREIGN KEY fk_csh_prev_status` | Pre-transition status code. |
| `new_status_code` | `VARCHAR(32)` | No | None | `FOREIGN KEY fk_csh_new_status` | Post-transition status code. |
| `transition_timestamp`| `DATETIME(6)` | No | `CURRENT_TIMESTAMP(6)` | None | Event timestamp (UTC). |
| `transition_reason` | `VARCHAR(255)` | Yes | `NULL` | None | Operational driver for transition. |
| `actor_reference` | `VARCHAR(100)` | No | `'SYSTEM'` | None | User or automated process identifier. |

---

### 5. Financial & Reconciliation Domain Tables

#### `remittances`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `remittance_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `remittance_reference`| `VARCHAR(64)` | No | None | `UNIQUE KEY uq_remit_ref` | Business identifier (e.g., `REM-001`). |
| `payer_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_remit_payers` | Disbursing payer. |
| `check_trace_number` | `VARCHAR(64)` | No | None | `UNIQUE KEY uq_remit_trace` | Payer check or EFT trace reference. |
| `payment_method` | `VARCHAR(32)` | No | `'EFT'` | None | Disbursement method (`EFT`, `CHECK`, `VIRTUAL_CARD`). |
| `total_paid_amount` | `DECIMAL(12, 2)`| No | `0.00` | `CHECK (total_paid_amount >= 0.00)` | Total cash value of remittance batch. |
| `remittance_date` | `DATE` | No | None | None | Date of financial issuance. |

#### `payments`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `payment_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `payment_reference` | `VARCHAR(64)` | No | None | `UNIQUE KEY uq_pmt_ref` | Business identifier (e.g., `PMT-001`). |
| `remittance_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_pmt_remit` | Parent remittance transaction. |
| `claim_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_pmt_claims` | Settled claim header. |
| `paid_amount` | `DECIMAL(12, 2)`| No | `0.00` | `CHECK (paid_amount >= 0.00)` | Specific cash amount applied to claim. |
| `payment_date` | `DATE` | No | None | None | Cash receipt date. |

#### `adjustments`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `adjustment_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `claim_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_adj_claims` | Adjusted claim header. |
| `claim_line_id` | `BIGINT UNSIGNED` | Yes | `NULL` | `FOREIGN KEY fk_adj_lines` | Optional specific line item adjusted. |
| `group_code` | `VARCHAR(8)` | No | None | `FOREIGN KEY fk_adj_group` | CARC group (`CO`, `PR`, `OA`, etc.). |
| `reason_code` | `VARCHAR(16)` | No | None | None | Specific CARC reason code (e.g., `45`, `97`, `1`). |
| `adjustment_amount` | `DECIMAL(12, 2)`| No | `0.00` | `CHECK (adjustment_amount >= 0.00)` | Contractual reduction amount. |
| `adjustment_description`| `VARCHAR(255)`| Yes | `NULL` | None | Plain-text explanation. |

#### `denials`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `denial_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `claim_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_den_claims` | Denied claim header. |
| `claim_line_id` | `BIGINT UNSIGNED` | Yes | `NULL` | `FOREIGN KEY fk_den_lines` | Optional specific line item denied. |
| `denial_code` | `VARCHAR(16)` | No | None | None | Payer denial reason code (e.g., `CO-16`). |
| `denial_reason` | `VARCHAR(255)` | No | None | None | Detailed description of denial reason. |
| `denial_date` | `DATE` | No | None | None | Date denial determination occurred. |
| `is_appealable` | `BOOLEAN` | No | `1` | None | Flag indicating if appeal pathway exists. |

#### `reconciliations`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `reconciliation_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `claim_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_rec_claims` | Reconciled claim header. |
| `total_billed` | `DECIMAL(12, 2)`| No | `0.00` | None | Snapshot of total billed amount. |
| `total_paid` | `DECIMAL(12, 2)`| No | `0.00` | None | Total cumulative payments recorded. |
| `total_adjusted` | `DECIMAL(12, 2)`| No | `0.00` | None | Total contractual adjustments recorded. |
| `total_patient_resp`| `DECIMAL(12, 2)`| No | `0.00` | None | Patient deductible/coinsurance total. |
| `variance_amount` | `DECIMAL(12, 2)`| No | `0.00` | None | $\text{Billed} - (\text{Paid} + \text{Adj} + \text{PatResp})$. |
| `reconciliation_status`| `VARCHAR(32)`| No | `'UNBALANCED'` | None | Status (`BALANCED`, `UNBALANCED`, `DISPUTED`). |
| `reconciled_at` | `DATETIME(6)` | No | `CURRENT_TIMESTAMP(6)` | None | Verification timestamp (UTC). |

---

### 6. Operations & Issue Management Tables

#### `issues`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `issue_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `issue_reference` | `VARCHAR(64)` | No | None | `UNIQUE KEY uq_issues_ref` | Business identifier (e.g., `ISS-000491`). |
| `rule_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_issues_rules` | Triggering QA validation rule. |
| `claim_id` | `BIGINT UNSIGNED` | Yes | `NULL` | `FOREIGN KEY fk_issues_claims` | Linked defective claim (if claim-specific). |
| `dimension_code` | `VARCHAR(32)` | No | None | `FOREIGN KEY fk_issues_dim` | Primary data quality dimension. |
| `severity_code` | `VARCHAR(16)` | No | None | `FOREIGN KEY fk_issues_sev` | Assigned severity (`Critical`–`Low`). |
| `current_status_code`| `VARCHAR(32)` | No | `'Detected'` | `FOREIGN KEY fk_issues_status` | Lifecycle position. |
| `assigned_to_user` | `VARCHAR(100)` | Yes | `NULL` | None | Analyst username / owner. |
| `detected_at` | `DATETIME(6)` | No | `CURRENT_TIMESTAMP(6)` | None | Timestamp anomaly was flagged. |
| `resolved_at` | `DATETIME(6)` | Yes | `NULL` | None | Timestamp of verified closure. |
| `root_cause_code` | `VARCHAR(64)` | Yes | `NULL` | `FOREIGN KEY fk_issues_rc` | Confirmed root-cause category. |
| `variance_amount` | `DECIMAL(12, 2)`| Yes | `NULL` | None | Financial dollar amount at risk. |

#### `issue_history`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `history_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `issue_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_ih_issues` | Target issue. |
| `previous_status_code`| `VARCHAR(32)` | Yes | `NULL` | `FOREIGN KEY fk_ih_prev_status` | Pre-transition status code. |
| `new_status_code` | `VARCHAR(32)` | No | None | `FOREIGN KEY fk_ih_new_status` | Post-transition status code. |
| `transition_timestamp`| `DATETIME(6)` | No | `CURRENT_TIMESTAMP(6)` | None | Event timestamp (UTC). |
| `actor_user` | `VARCHAR(100)` | No | None | None | User executing state update. |
| `transition_notes` | `TEXT` | Yes | `NULL` | None | Mandatory justification notes. |

#### `issue_notes`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `note_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `issue_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_in_issues` | Target issue. |
| `author_user` | `VARCHAR(100)` | No | None | None | Note author username. |
| `note_text` | `TEXT` | No | None | None | Markdown-formatted investigation note. |
| `is_internal` | `BOOLEAN` | No | `1` | None | Visibility flag. |
| `created_at` | `DATETIME(6)` | No | `CURRENT_TIMESTAMP(6)` | None | Timestamp created (UTC). |

---

### 7. QA Engine Metadata Tables

#### `qa_rule_categories`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `category_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `category_code` | `VARCHAR(32)` | No | None | `UNIQUE KEY uq_qarc_code` | Category code (e.g., `FINANCIAL`, `TEMPORAL`). |
| `category_name` | `VARCHAR(100)` | No | None | None | Descriptive title. |
| `description` | `VARCHAR(255)` | Yes | `NULL` | None | Scope summary. |

#### `qa_rules`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `rule_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `rule_code` | `VARCHAR(64)` | No | None | `UNIQUE KEY uq_qar_code` | Unique rule code (e.g., `RULE-FIN-001`). |
| `category_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_qar_cat` | Functional category. |
| `dimension_code` | `VARCHAR(32)` | No | None | `FOREIGN KEY fk_qar_dim` | Linked DQ dimension. |
| `default_severity_code`| `VARCHAR(16)`| No | None | `FOREIGN KEY fk_qar_sev` | Initial severity triage rating. |
| `rule_name` | `VARCHAR(150)` | No | None | None | Rule display title. |
| `description` | `TEXT` | No | None | None | Human-readable explanation & SOP. |
| `sql_logic` | `TEXT` | No | None | None | Executable SQL query specification. |
| `is_active` | `BOOLEAN` | No | `1` | None | Active/inactive execution toggle. |

#### `qa_execution_runs`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `run_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `run_reference` | `VARCHAR(64)` | No | None | `UNIQUE KEY uq_qrun_ref` | Batch run reference (e.g., `RUN-20260821-01`). |
| `batch_identifier` | `VARCHAR(64)` | No | None | None | Source synthetic batch tag. |
| `started_at` | `DATETIME(6)` | No | None | None | Execution start timestamp (UTC). |
| `completed_at` | `DATETIME(6)` | Yes | `NULL` | None | Execution completion timestamp (UTC). |
| `status` | `VARCHAR(32)` | No | `'RUNNING'` | None | Status (`RUNNING`, `COMPLETED`, `FAILED`). |
| `total_rules_evaluated`| `INT UNSIGNED` | No | `0` | None | Count of rules run. |
| `total_records_evaluated`| `BIGINT UNSIGNED`| No | `0` | None | Count of rows scanned. |
| `total_issues_detected`| `INT UNSIGNED` | No | `0` | None | Count of new anomalies flagged. |
| `dq_score` | `DECIMAL(5, 2)` | Yes | `NULL` | None | Aggregate batch DQ score (0.00–100.00). |

#### `qa_results`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `result_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `run_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_qres_run` | Linked batch execution run. |
| `rule_id` | `BIGINT UNSIGNED` | No | None | `FOREIGN KEY fk_qres_rule` | Specific rule evaluated. |
| `records_evaluated`| `BIGINT UNSIGNED`| No | `0` | None | Rows checked by this rule. |
| `issues_detected` | `INT UNSIGNED` | No | `0` | None | Count of violations found. |
| `execution_duration_ms`| `INT UNSIGNED`| No | `0` | None | Query execution time in milliseconds. |
| `run_status` | `VARCHAR(32)` | No | `'SUCCESS'` | None | Outcome (`SUCCESS`, `ERROR`, `TIMEOUT`). |

---

### 8. Audit & Governance Tables

#### `audit_events`
| Column Name | MySQL Data Type | Nullable | Default | Constraints / Keys | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `audit_id` | `BIGINT UNSIGNED` | No | None | `PRIMARY KEY AUTO_INCREMENT` | Internal surrogate identifier. |
| `event_timestamp` | `DATETIME(6)` | No | `CURRENT_TIMESTAMP(6)` | None | Event timestamp (UTC). |
| `actor_user` | `VARCHAR(100)` | No | None | None | Executing user username / system ID. |
| `action_type` | `VARCHAR(64)` | No | None | None | Action (`CLAIM_STATUS_UPDATE`, `ISSUE_RESOLVED`, etc.). |
| `entity_type` | `VARCHAR(64)` | No | None | None | Target entity (`CLAIM`, `ISSUE`, `RULE`). |
| `entity_id` | `VARCHAR(64)` | No | None | None | Business or database ID of target entity. |
| `previous_state_json`| `JSON` | Yes | `NULL` | None | JSON snapshot of data prior to change. |
| `new_state_json` | `JSON` | Yes | `NULL` | None | JSON snapshot of data after change. |
| `ip_address` | `VARCHAR(45)` | Yes | `NULL` | None | Client IP address (IPv4 or IPv6). |

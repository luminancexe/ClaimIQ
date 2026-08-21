# ClaimIQ — Entity-Relationship Diagram (ERD) Specification

## 1. High-Level System ER Diagram

This diagram visualizes the primary relational connections across all nine domains of the ClaimIQ MySQL 8.x database.

```mermaid
erDiagram
    PATIENTS ||--o{ ENCOUNTERS : experiences
    PROVIDERS ||--o{ ENCOUNTERS : renders
    FACILITIES ||--o{ ENCOUNTERS : hosts
    
    PAYERS ||--o{ INSURANCE_PLANS : offers
    INSURANCE_PLANS ||--o{ PATIENT_COVERAGE : covers
    PATIENTS ||--o{ PATIENT_COVERAGE : enrolls
    
    ENCOUNTERS ||--o{ ENCOUNTER_DIAGNOSES : contains
    ENCOUNTERS ||--o{ CLAIMS : generates
    
    CLAIMS ||--|{ CLAIM_LINES : itemizes
    CLAIMS ||--o{ CLAIM_STATUS_HISTORY : tracks
    
    REMITTANCES ||--o{ PAYMENTS : bundles
    CLAIMS ||--o{ PAYMENTS : settles
    CLAIMS ||--o{ ADJUSTMENTS : adjusts
    CLAIMS ||--o{ DENIALS : records
    CLAIMS ||--o{ RECONCILIATIONS : balances
    
    QA_RULE_CATEGORIES ||--o{ QA_RULES : categorizes
    QA_RULES ||--o{ QA_RESULTS : produces
    QA_EXECUTION_RUNS ||--o{ QA_RESULTS : executes
    
    QA_RULES ||--o{ ISSUES : detects
    CLAIMS ||--o{ ISSUES : flags
    ISSUES ||--o{ ISSUE_HISTORY : logs
    ISSUES ||--o{ ISSUE_NOTES : documents
    
    AUDIT_EVENTS }o--|| USERS : captures
```

---

## 2. Domain-Specific ER Diagrams

### 2.1 Patient, Provider, Facility & Insurance Coverage

```mermaid
erDiagram
    PATIENTS {
        BIGINT_UNSIGNED patient_id PK
        VARCHAR_64 patient_reference UK
        VARCHAR_100 first_name
        VARCHAR_100 last_name
        DATE date_of_birth
        VARCHAR_16 gender
        VARCHAR_2 address_state
        DATETIME_6 created_at
    }

    FACILITIES {
        BIGINT_UNSIGNED facility_id PK
        VARCHAR_64 facility_reference UK
        VARCHAR_150 facility_name
        VARCHAR_10 tin
        VARCHAR_50 facility_type
        VARCHAR_2 state
    }

    PROVIDERS {
        BIGINT_UNSIGNED provider_id PK
        VARCHAR_64 provider_reference UK
        BIGINT_UNSIGNED facility_id FK
        VARCHAR_100 first_name
        VARCHAR_100 last_name
        VARCHAR_10 npi UK
        VARCHAR_10 taxonomy_code
        VARCHAR_100 specialty
    }

    PAYERS {
        BIGINT_UNSIGNED payer_id PK
        VARCHAR_64 payer_reference UK
        VARCHAR_150 payer_name
        VARCHAR_50 payer_type
        INT timely_filing_days
    }

    INSURANCE_PLANS {
        BIGINT_UNSIGNED plan_id PK
        BIGINT_UNSIGNED payer_id FK
        VARCHAR_150 plan_name
        VARCHAR_50 plan_type
    }

    PATIENT_COVERAGE {
        BIGINT_UNSIGNED coverage_id PK
        BIGINT_UNSIGNED patient_id FK
        BIGINT_UNSIGNED plan_id FK
        VARCHAR_64 member_id
        VARCHAR_64 group_number
        DATE effective_date
        DATE termination_date
        BOOLEAN is_primary
    }

    PATIENTS ||--o{ PATIENT_COVERAGE : has
    INSURANCE_PLANS ||--o{ PATIENT_COVERAGE : provides
    PAYERS ||--o{ INSURANCE_PLANS : sponsors
    FACILITIES ||--o{ PROVIDERS : employs
```

---

### 2.2 Encounters, Diagnoses & Claims Itemization

```mermaid
erDiagram
    ENCOUNTERS {
        BIGINT_UNSIGNED encounter_id PK
        VARCHAR_64 encounter_reference UK
        BIGINT_UNSIGNED patient_id FK
        BIGINT_UNSIGNED provider_id FK
        BIGINT_UNSIGNED facility_id FK
        DATE date_of_service
        VARCHAR_50 encounter_type
        DATE discharge_date
    }

    ENCOUNTER_DIAGNOSES {
        BIGINT_UNSIGNED diagnosis_id PK
        BIGINT_UNSIGNED encounter_id FK
        VARCHAR_16 icd10_code
        VARCHAR_255 diagnosis_description
        BOOLEAN is_primary
        INT sequence_number
    }

    CLAIMS {
        BIGINT_UNSIGNED claim_id PK
        VARCHAR_64 claim_reference UK
        BIGINT_UNSIGNED encounter_id FK
        BIGINT_UNSIGNED patient_id FK
        BIGINT_UNSIGNED billing_provider_id FK
        BIGINT_UNSIGNED payer_id FK
        VARCHAR_32 current_status_code FK
        DECIMAL_12_2 total_billed_amount
        DATE submission_date
        DATE adjudication_date
        BOOLEAN is_reconciled
    }

    CLAIM_LINES {
        BIGINT_UNSIGNED claim_line_id PK
        BIGINT_UNSIGNED claim_id FK
        INT line_number
        VARCHAR_16 cpt_code
        VARCHAR_255 procedure_description
        DECIMAL_8_2 units
        DECIMAL_12_2 unit_price
        DECIMAL_12_2 line_billed_amount
        VARCHAR_32 line_status
    }

    CLAIM_STATUS_HISTORY {
        BIGINT_UNSIGNED history_id PK
        BIGINT_UNSIGNED claim_id FK
        VARCHAR_32 previous_status_code FK
        VARCHAR_32 new_status_code FK
        DATETIME_6 transition_timestamp
        VARCHAR_255 transition_reason
        VARCHAR_100 actor_reference
    }

    ENCOUNTERS ||--o{ ENCOUNTER_DIAGNOSES : includes
    ENCOUNTERS ||--o{ CLAIMS : originates
    CLAIMS ||--|{ CLAIM_LINES : itemizes
    CLAIMS ||--o{ CLAIM_STATUS_HISTORY : records
```

---

### 2.3 Financial, Payment & Reconciliation Domain

```mermaid
erDiagram
    REMITTANCES {
        BIGINT_UNSIGNED remittance_id PK
        VARCHAR_64 remittance_reference UK
        BIGINT_UNSIGNED payer_id FK
        VARCHAR_64 check_trace_number UK
        VARCHAR_32 payment_method
        DECIMAL_12_2 total_paid_amount
        DATE remittance_date
    }

    PAYMENTS {
        BIGINT_UNSIGNED payment_id PK
        VARCHAR_64 payment_reference UK
        BIGINT_UNSIGNED remittance_id FK
        BIGINT_UNSIGNED claim_id FK
        DECIMAL_12_2 paid_amount
        DATE payment_date
    }

    ADJUSTMENTS {
        BIGINT_UNSIGNED adjustment_id PK
        BIGINT_UNSIGNED claim_id FK
        BIGINT_UNSIGNED claim_line_id FK
        VARCHAR_8 group_code FK
        VARCHAR_16 reason_code
        DECIMAL_12_2 adjustment_amount
        VARCHAR_255 adjustment_description
    }

    DENIALS {
        BIGINT_UNSIGNED denial_id PK
        BIGINT_UNSIGNED claim_id FK
        BIGINT_UNSIGNED claim_line_id FK
        VARCHAR_16 denial_code
        VARCHAR_255 denial_reason
        DATE denial_date
        BOOLEAN is_appealable
    }

    RECONCILIATIONS {
        BIGINT_UNSIGNED reconciliation_id PK
        BIGINT_UNSIGNED claim_id FK
        DECIMAL_12_2 total_billed
        DECIMAL_12_2 total_paid
        DECIMAL_12_2 total_adjusted
        DECIMAL_12_2 total_patient_resp
        DECIMAL_12_2 variance_amount
        VARCHAR_32 reconciliation_status
        DATETIME_6 reconciled_at
    }

    REMITTANCES ||--o{ PAYMENTS : contains
    CLAIMS ||--o{ PAYMENTS : receives
    CLAIMS ||--o{ ADJUSTMENTS : applies
    CLAIMS ||--o{ DENIALS : flags
    CLAIMS ||--o{ RECONCILIATIONS : balances
```

---

### 2.4 Operations, QA Engine & Audit Domain

```mermaid
erDiagram
    QA_RULES {
        BIGINT_UNSIGNED rule_id PK
        VARCHAR_64 rule_code UK
        BIGINT_UNSIGNED category_id FK
        VARCHAR_32 dimension_code FK
        VARCHAR_16 default_severity_code FK
        VARCHAR_150 rule_name
        TEXT description
        TEXT sql_logic
        BOOLEAN is_active
    }

    ISSUES {
        BIGINT_UNSIGNED issue_id PK
        VARCHAR_64 issue_reference UK
        BIGINT_UNSIGNED rule_id FK
        BIGINT_UNSIGNED claim_id FK
        VARCHAR_32 dimension_code FK
        VARCHAR_16 severity_code FK
        VARCHAR_32 current_status_code FK
        VARCHAR_100 assigned_to_user
        DATETIME_6 detected_at
        DATETIME_6 resolved_at
        VARCHAR_64 root_cause_code FK
        DECIMAL_12_2 variance_amount
    }

    ISSUE_HISTORY {
        BIGINT_UNSIGNED history_id PK
        BIGINT_UNSIGNED issue_id FK
        VARCHAR_32 previous_status_code FK
        VARCHAR_32 new_status_code FK
        DATETIME_6 transition_timestamp
        VARCHAR_100 actor_user
        TEXT transition_notes
    }

    ISSUE_NOTES {
        BIGINT_UNSIGNED note_id PK
        BIGINT_UNSIGNED issue_id FK
        VARCHAR_100 author_user
        TEXT note_text
        BOOLEAN is_internal
        DATETIME_6 created_at
    }

    AUDIT_EVENTS {
        BIGINT_UNSIGNED audit_id PK
        DATETIME_6 event_timestamp
        VARCHAR_100 actor_user
        VARCHAR_64 action_type
        VARCHAR_64 entity_type
        VARCHAR_64 entity_id
        JSON previous_state_json
        JSON new_state_json
        VARCHAR_45 ip_address
    }

    QA_RULES ||--o{ ISSUES : creates
    ISSUES ||--o{ ISSUE_HISTORY : tracks
    ISSUES ||--o{ ISSUE_NOTES : contains
```

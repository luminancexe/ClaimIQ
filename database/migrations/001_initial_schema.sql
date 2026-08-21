-- ============================================================================
-- ClaimIQ Database Migration: 001_initial_schema.sql
-- Target Database: MySQL 8.x
-- Storage Engine: InnoDB
-- Character Set: utf8mb4 / Collation: utf8mb4_0900_ai_ci
-- Timezone Standard: Canonical UTC (DATETIME(6))
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- 1. Reference Domain Tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ref_claim_statuses (
    status_code VARCHAR(32) NOT NULL,
    status_name VARCHAR(64) NOT NULL,
    description VARCHAR(255) NOT NULL,
    is_terminal BOOLEAN NOT NULL DEFAULT 0,
    CONSTRAINT pk_ref_claim_statuses PRIMARY KEY (status_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ref_issue_statuses (
    status_code VARCHAR(32) NOT NULL,
    status_name VARCHAR(64) NOT NULL,
    description VARCHAR(255) NOT NULL,
    is_terminal BOOLEAN NOT NULL DEFAULT 0,
    CONSTRAINT pk_ref_issue_statuses PRIMARY KEY (status_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ref_severities (
    severity_code VARCHAR(16) NOT NULL,
    severity_name VARCHAR(32) NOT NULL,
    sla_hours INT UNSIGNED NOT NULL DEFAULT 24,
    priority_rank TINYINT UNSIGNED NOT NULL DEFAULT 1,
    CONSTRAINT pk_ref_severities PRIMARY KEY (severity_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ref_dq_dimensions (
    dimension_code VARCHAR(32) NOT NULL,
    dimension_name VARCHAR(64) NOT NULL,
    weight DECIMAL(4, 2) NOT NULL DEFAULT 0.10,
    description VARCHAR(255) NOT NULL,
    CONSTRAINT pk_ref_dq_dimensions PRIMARY KEY (dimension_code),
    CONSTRAINT chk_ref_dq_dim_weight CHECK (weight >= 0.00 AND weight <= 1.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ref_root_causes (
    root_cause_code VARCHAR(64) NOT NULL,
    root_cause_name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    CONSTRAINT pk_ref_root_causes PRIMARY KEY (root_cause_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ref_adjustment_group_codes (
    group_code VARCHAR(8) NOT NULL,
    group_name VARCHAR(64) NOT NULL,
    description VARCHAR(255) NOT NULL,
    CONSTRAINT pk_ref_adj_group_codes PRIMARY KEY (group_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 2. Patient & Provider Domain Tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS patients (
    patient_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    patient_reference VARCHAR(64) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(16) NOT NULL,
    address_state VARCHAR(2) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_patients PRIMARY KEY (patient_id),
    CONSTRAINT uq_patients_ref UNIQUE KEY (patient_reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS facilities (
    facility_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    facility_reference VARCHAR(64) NOT NULL,
    facility_name VARCHAR(150) NOT NULL,
    tin VARCHAR(10) NOT NULL,
    facility_type VARCHAR(50) NOT NULL,
    state VARCHAR(2) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_facilities PRIMARY KEY (facility_id),
    CONSTRAINT uq_facilities_ref UNIQUE KEY (facility_reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS providers (
    provider_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    provider_reference VARCHAR(64) NOT NULL,
    facility_id BIGINT UNSIGNED NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    npi VARCHAR(10) NOT NULL,
    taxonomy_code VARCHAR(10) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_providers PRIMARY KEY (provider_id),
    CONSTRAINT uq_providers_ref UNIQUE KEY (provider_reference),
    CONSTRAINT uq_providers_npi UNIQUE KEY (npi),
    CONSTRAINT fk_providers_facilities FOREIGN KEY (facility_id) REFERENCES facilities (facility_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS payers (
    payer_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    payer_reference VARCHAR(64) NOT NULL,
    payer_name VARCHAR(150) NOT NULL,
    payer_type VARCHAR(50) NOT NULL,
    timely_filing_days INT UNSIGNED NOT NULL DEFAULT 365,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_payers PRIMARY KEY (payer_id),
    CONSTRAINT uq_payers_ref UNIQUE KEY (payer_reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS insurance_plans (
    plan_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    payer_id BIGINT UNSIGNED NOT NULL,
    plan_name VARCHAR(150) NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_insurance_plans PRIMARY KEY (plan_id),
    CONSTRAINT fk_plans_payers FOREIGN KEY (payer_id) REFERENCES payers (payer_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS patient_coverage (
    coverage_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    patient_id BIGINT UNSIGNED NOT NULL,
    plan_id BIGINT UNSIGNED NOT NULL,
    member_id VARCHAR(64) NOT NULL,
    group_number VARCHAR(64) NULL,
    effective_date DATE NOT NULL,
    termination_date DATE NULL,
    is_primary BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_patient_coverage PRIMARY KEY (coverage_id),
    CONSTRAINT fk_cov_patients FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cov_plans FOREIGN KEY (plan_id) REFERENCES insurance_plans (plan_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 3. Clinical & Encounter Domain Tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS encounters (
    encounter_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    encounter_reference VARCHAR(64) NOT NULL,
    patient_id BIGINT UNSIGNED NOT NULL,
    provider_id BIGINT UNSIGNED NOT NULL,
    facility_id BIGINT UNSIGNED NOT NULL,
    date_of_service DATE NOT NULL,
    encounter_type VARCHAR(50) NOT NULL,
    discharge_date DATE NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_encounters PRIMARY KEY (encounter_id),
    CONSTRAINT uq_encounters_ref UNIQUE KEY (encounter_reference),
    CONSTRAINT fk_enc_patients FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_enc_providers FOREIGN KEY (provider_id) REFERENCES providers (provider_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_enc_facilities FOREIGN KEY (facility_id) REFERENCES facilities (facility_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS encounter_diagnoses (
    diagnosis_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    encounter_id BIGINT UNSIGNED NOT NULL,
    icd10_code VARCHAR(16) NOT NULL,
    diagnosis_description VARCHAR(255) NULL,
    is_primary BOOLEAN NOT NULL DEFAULT 0,
    sequence_number INT UNSIGNED NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_encounter_diagnoses PRIMARY KEY (diagnosis_id),
    CONSTRAINT fk_diag_encounters FOREIGN KEY (encounter_id) REFERENCES encounters (encounter_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 4. Claims Domain Tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS claims (
    claim_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    claim_reference VARCHAR(64) NOT NULL,
    encounter_id BIGINT UNSIGNED NOT NULL,
    patient_id BIGINT UNSIGNED NOT NULL,
    billing_provider_id BIGINT UNSIGNED NOT NULL,
    payer_id BIGINT UNSIGNED NOT NULL,
    current_status_code VARCHAR(32) NOT NULL DEFAULT 'Submitted',
    total_billed_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    submission_date DATE NOT NULL,
    adjudication_date DATE NULL,
    is_reconciled BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_claims PRIMARY KEY (claim_id),
    CONSTRAINT uq_claims_ref UNIQUE KEY (claim_reference),
    CONSTRAINT fk_claims_encounters FOREIGN KEY (encounter_id) REFERENCES encounters (encounter_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_claims_patients FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_claims_providers FOREIGN KEY (billing_provider_id) REFERENCES providers (provider_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_claims_payers FOREIGN KEY (payer_id) REFERENCES payers (payer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_claims_status FOREIGN KEY (current_status_code) REFERENCES ref_claim_statuses (status_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_claims_total_billed_amt CHECK (total_billed_amount >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS claim_lines (
    claim_line_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    claim_id BIGINT UNSIGNED NOT NULL,
    line_number INT UNSIGNED NOT NULL DEFAULT 1,
    cpt_code VARCHAR(16) NOT NULL,
    procedure_description VARCHAR(255) NULL,
    units DECIMAL(8, 2) NOT NULL DEFAULT 1.00,
    unit_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    line_billed_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    line_status VARCHAR(32) NOT NULL DEFAULT 'Submitted',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_claim_lines PRIMARY KEY (claim_line_id),
    CONSTRAINT fk_lines_claims FOREIGN KEY (claim_id) REFERENCES claims (claim_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_claim_lines_units CHECK (units > 0.00),
    CONSTRAINT chk_claim_lines_unit_price CHECK (unit_price >= 0.00),
    CONSTRAINT chk_claim_lines_line_billed CHECK (line_billed_amount >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS claim_status_history (
    history_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    claim_id BIGINT UNSIGNED NOT NULL,
    previous_status_code VARCHAR(32) NULL,
    new_status_code VARCHAR(32) NOT NULL,
    transition_timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    transition_reason VARCHAR(255) NULL,
    actor_reference VARCHAR(100) NOT NULL DEFAULT 'SYSTEM',
    CONSTRAINT pk_claim_status_history PRIMARY KEY (history_id),
    CONSTRAINT fk_csh_claims FOREIGN KEY (claim_id) REFERENCES claims (claim_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_csh_prev_status FOREIGN KEY (previous_status_code) REFERENCES ref_claim_statuses (status_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_csh_new_status FOREIGN KEY (new_status_code) REFERENCES ref_claim_statuses (status_code) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 5. Financial & Reconciliation Domain Tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS remittances (
    remittance_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    remittance_reference VARCHAR(64) NOT NULL,
    payer_id BIGINT UNSIGNED NOT NULL,
    check_trace_number VARCHAR(64) NOT NULL,
    payment_method VARCHAR(32) NOT NULL DEFAULT 'EFT',
    total_paid_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    remittance_date DATE NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_remittances PRIMARY KEY (remittance_id),
    CONSTRAINT uq_remit_ref UNIQUE KEY (remittance_reference),
    CONSTRAINT uq_remit_trace UNIQUE KEY (check_trace_number),
    CONSTRAINT fk_remit_payers FOREIGN KEY (payer_id) REFERENCES payers (payer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_remit_total_paid CHECK (total_paid_amount >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS payments (
    payment_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    payment_reference VARCHAR(64) NOT NULL,
    remittance_id BIGINT UNSIGNED NOT NULL,
    claim_id BIGINT UNSIGNED NOT NULL,
    paid_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    payment_date DATE NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_payments PRIMARY KEY (payment_id),
    CONSTRAINT uq_pmt_ref UNIQUE KEY (payment_reference),
    CONSTRAINT fk_pmt_remit FOREIGN KEY (remittance_id) REFERENCES remittances (remittance_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_pmt_claims FOREIGN KEY (claim_id) REFERENCES claims (claim_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_payments_paid_amt CHECK (paid_amount >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS adjustments (
    adjustment_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    claim_id BIGINT UNSIGNED NOT NULL,
    claim_line_id BIGINT UNSIGNED NULL,
    group_code VARCHAR(8) NOT NULL,
    reason_code VARCHAR(16) NOT NULL,
    adjustment_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    adjustment_description VARCHAR(255) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_adjustments PRIMARY KEY (adjustment_id),
    CONSTRAINT fk_adj_claims FOREIGN KEY (claim_id) REFERENCES claims (claim_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_adj_lines FOREIGN KEY (claim_line_id) REFERENCES claim_lines (claim_line_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_adj_group FOREIGN KEY (group_code) REFERENCES ref_adjustment_group_codes (group_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_adj_amount CHECK (adjustment_amount >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS denials (
    denial_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    claim_id BIGINT UNSIGNED NOT NULL,
    claim_line_id BIGINT UNSIGNED NULL,
    denial_code VARCHAR(16) NOT NULL,
    denial_reason VARCHAR(255) NOT NULL,
    denial_date DATE NOT NULL,
    is_appealable BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_denials PRIMARY KEY (denial_id),
    CONSTRAINT fk_den_claims FOREIGN KEY (claim_id) REFERENCES claims (claim_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_den_lines FOREIGN KEY (claim_line_id) REFERENCES claim_lines (claim_line_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS reconciliations (
    reconciliation_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    claim_id BIGINT UNSIGNED NOT NULL,
    total_billed DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    total_paid DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    total_adjusted DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    total_patient_resp DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    variance_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    reconciliation_status VARCHAR(32) NOT NULL DEFAULT 'UNBALANCED',
    reconciled_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_reconciliations PRIMARY KEY (reconciliation_id),
    CONSTRAINT uq_rec_claim UNIQUE KEY (claim_id),
    CONSTRAINT fk_rec_claims FOREIGN KEY (claim_id) REFERENCES claims (claim_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 6. Operations & QA Domain Tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS qa_rule_categories (
    category_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    category_code VARCHAR(32) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_qa_rule_categories PRIMARY KEY (category_id),
    CONSTRAINT uq_qarc_code UNIQUE KEY (category_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS qa_rules (
    rule_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    rule_code VARCHAR(64) NOT NULL,
    category_id BIGINT UNSIGNED NOT NULL,
    dimension_code VARCHAR(32) NOT NULL,
    default_severity_code VARCHAR(16) NOT NULL,
    rule_name VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    sql_logic TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_qa_rules PRIMARY KEY (rule_id),
    CONSTRAINT uq_qar_code UNIQUE KEY (rule_code),
    CONSTRAINT fk_qar_cat FOREIGN KEY (category_id) REFERENCES qa_rule_categories (category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_qar_dim FOREIGN KEY (dimension_code) REFERENCES ref_dq_dimensions (dimension_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_qar_sev FOREIGN KEY (default_severity_code) REFERENCES ref_severities (severity_code) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS qa_execution_runs (
    run_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    run_reference VARCHAR(64) NOT NULL,
    batch_identifier VARCHAR(64) NOT NULL,
    started_at DATETIME(6) NOT NULL,
    completed_at DATETIME(6) NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'RUNNING',
    total_rules_evaluated INT UNSIGNED NOT NULL DEFAULT 0,
    total_records_evaluated BIGINT UNSIGNED NOT NULL DEFAULT 0,
    total_issues_detected INT UNSIGNED NOT NULL DEFAULT 0,
    dq_score DECIMAL(5, 2) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_qa_execution_runs PRIMARY KEY (run_id),
    CONSTRAINT uq_qrun_ref UNIQUE KEY (run_reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS qa_results (
    result_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    run_id BIGINT UNSIGNED NOT NULL,
    rule_id BIGINT UNSIGNED NOT NULL,
    records_evaluated BIGINT UNSIGNED NOT NULL DEFAULT 0,
    issues_detected INT UNSIGNED NOT NULL DEFAULT 0,
    execution_duration_ms INT UNSIGNED NOT NULL DEFAULT 0,
    run_status VARCHAR(32) NOT NULL DEFAULT 'SUCCESS',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_qa_results PRIMARY KEY (result_id),
    CONSTRAINT fk_qres_run FOREIGN KEY (run_id) REFERENCES qa_execution_runs (run_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_qres_rule FOREIGN KEY (rule_id) REFERENCES qa_rules (rule_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS issues (
    issue_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    issue_reference VARCHAR(64) NOT NULL,
    rule_id BIGINT UNSIGNED NOT NULL,
    claim_id BIGINT UNSIGNED NULL,
    dimension_code VARCHAR(32) NOT NULL,
    severity_code VARCHAR(16) NOT NULL,
    current_status_code VARCHAR(32) NOT NULL DEFAULT 'Detected',
    assigned_to_user VARCHAR(100) NULL,
    detected_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    resolved_at DATETIME(6) NULL,
    root_cause_code VARCHAR(64) NULL,
    variance_amount DECIMAL(12, 2) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_issues PRIMARY KEY (issue_id),
    CONSTRAINT uq_issues_ref UNIQUE KEY (issue_reference),
    CONSTRAINT fk_issues_rules FOREIGN KEY (rule_id) REFERENCES qa_rules (rule_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_issues_claims FOREIGN KEY (claim_id) REFERENCES claims (claim_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_issues_dim FOREIGN KEY (dimension_code) REFERENCES ref_dq_dimensions (dimension_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_issues_sev FOREIGN KEY (severity_code) REFERENCES ref_severities (severity_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_issues_status FOREIGN KEY (current_status_code) REFERENCES ref_issue_statuses (status_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_issues_rc FOREIGN KEY (root_cause_code) REFERENCES ref_root_causes (root_cause_code) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS issue_history (
    history_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    issue_id BIGINT UNSIGNED NOT NULL,
    previous_status_code VARCHAR(32) NULL,
    new_status_code VARCHAR(32) NOT NULL,
    transition_timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    actor_user VARCHAR(100) NOT NULL,
    transition_notes TEXT NULL,
    CONSTRAINT pk_issue_history PRIMARY KEY (history_id),
    CONSTRAINT fk_ih_issues FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ih_prev_status FOREIGN KEY (previous_status_code) REFERENCES ref_issue_statuses (status_code) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_ih_new_status FOREIGN KEY (new_status_code) REFERENCES ref_issue_statuses (status_code) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS issue_notes (
    note_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    issue_id BIGINT UNSIGNED NOT NULL,
    author_user VARCHAR(100) NOT NULL,
    note_text TEXT NOT NULL,
    is_internal BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT pk_issue_notes PRIMARY KEY (note_id),
    CONSTRAINT fk_in_issues FOREIGN KEY (issue_id) REFERENCES issues (issue_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 7. Audit & Governance Tables
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_events (
    audit_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    event_timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    actor_user VARCHAR(100) NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    previous_state_json JSON NULL,
    new_state_json JSON NULL,
    ip_address VARCHAR(45) NULL,
    CONSTRAINT pk_audit_events PRIMARY KEY (audit_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 8. Secondary B-Tree Indexes
-- ----------------------------------------------------------------------------

-- Provider & Facilities
CREATE INDEX idx_providers_facility ON providers (facility_id);

-- Encounters
CREATE INDEX idx_encounters_patient_dos ON encounters (patient_id, date_of_service);
CREATE INDEX idx_encounters_provider_dos ON encounters (provider_id, date_of_service);
CREATE INDEX idx_encounters_facility ON encounters (facility_id);

-- Diagnoses
CREATE INDEX idx_diagnoses_encounter ON encounter_diagnoses (encounter_id);
CREATE INDEX idx_diagnoses_icd10 ON encounter_diagnoses (icd10_code);

-- Coverage
CREATE INDEX idx_coverage_patient ON patient_coverage (patient_id);
CREATE INDEX idx_coverage_member ON patient_coverage (member_id);

-- Claims
CREATE INDEX idx_claims_patient ON claims (patient_id);
CREATE INDEX idx_claims_provider ON claims (billing_provider_id);
CREATE INDEX idx_claims_payer ON claims (payer_id);
CREATE INDEX idx_claims_status_sub ON claims (current_status_code, submission_date);
CREATE INDEX idx_claims_encounter ON claims (encounter_id);

-- Claim Lines
CREATE INDEX idx_claim_lines_claim_line ON claim_lines (claim_id, line_number);
CREATE INDEX idx_claim_lines_cpt ON claim_lines (cpt_code);

-- Claim Status History
CREATE INDEX idx_csh_claim_ts ON claim_status_history (claim_id, transition_timestamp);

-- Financial: Payments, Remittances, Adjustments, Denials
CREATE INDEX idx_remittances_payer ON remittances (payer_id);
CREATE INDEX idx_payments_claim ON payments (claim_id);
CREATE INDEX idx_payments_remit ON payments (remittance_id);
CREATE INDEX idx_adjustments_claim ON adjustments (claim_id);
CREATE INDEX idx_denials_claim ON denials (claim_id);

-- Operations & Issues
CREATE INDEX idx_issues_status_sev ON issues (current_status_code, severity_code);
CREATE INDEX idx_issues_claim ON issues (claim_id);
CREATE INDEX idx_issues_rule ON issues (rule_id);
CREATE INDEX idx_issues_assigned ON issues (assigned_to_user, current_status_code);
CREATE INDEX idx_issues_dim ON issues (dimension_code);
CREATE INDEX idx_issue_history_issue_ts ON issue_history (issue_id, transition_timestamp);
CREATE INDEX idx_issue_notes_issue_created ON issue_notes (issue_id, created_at);

-- QA Engine
CREATE INDEX idx_qa_rules_cat ON qa_rules (category_id);
CREATE INDEX idx_qa_results_run_rule ON qa_results (run_id, rule_id);

-- Audit Events
CREATE INDEX idx_audit_entity ON audit_events (entity_type, entity_id, event_timestamp);
CREATE INDEX idx_audit_actor_ts ON audit_events (actor_user, event_timestamp);

-- ----------------------------------------------------------------------------
-- 9. Seed Reference Data
-- ----------------------------------------------------------------------------

-- Reference Claim Statuses
INSERT INTO ref_claim_statuses (status_code, status_name, description, is_terminal) VALUES
('Submitted', 'Submitted', 'Claim electronically transmitted to payer/clearinghouse', 0),
('Accepted', 'Accepted', 'Claim passed front-end EDI validation and pre-adjudication edits', 0),
('Rejected', 'Rejected', 'Claim failed front-end EDI validation before adjudication', 0),
('Pending', 'Pending Review', 'Claim undergoing medical review or awaiting documentation', 0),
('Denied', 'Denied', 'Claim adjudicated and formally refused reimbursement', 1),
('Paid', 'Paid in Full', 'Claim adjudicated and fully paid per fee schedule', 1),
('Partially Paid', 'Partially Paid', 'Claim adjudicated with partial payment and contractual adjustment', 1)
ON DUPLICATE KEY UPDATE status_name = VALUES(status_name);

-- Reference Issue Statuses
INSERT INTO ref_issue_statuses (status_code, status_name, description, is_terminal) VALUES
('Detected', 'Detected', 'Anomaly identified by QA engine pending triage', 0),
('Open', 'Open', 'Issue queued in operational worklist awaiting assignment', 0),
('Investigating', 'In Investigation', 'Analyst actively inspecting root cause and context', 0),
('Resolved', 'Resolved', 'Defect verified and reconciled with root-cause documentation', 1),
('False Positive', 'False Positive', 'Investigated and confirmed as legitimate edge case', 1),
('Escalated', 'Escalated', 'Systemic bug or external payer issue requiring leadership', 0),
('Ignored', 'Ignored / Suppressed', 'Accepted non-blocking technical debt with manager approval', 1)
ON DUPLICATE KEY UPDATE status_name = VALUES(status_name);

-- Reference Severities
INSERT INTO ref_severities (severity_code, severity_name, sla_hours, priority_rank) VALUES
('Critical', 'Critical Severity', 4, 1),
('High', 'High Severity', 24, 2),
('Medium', 'Medium Severity', 72, 3),
('Low', 'Low Severity', 168, 4)
ON DUPLICATE KEY UPDATE sla_hours = VALUES(sla_hours);

-- Reference Data Quality Dimensions
INSERT INTO ref_dq_dimensions (dimension_code, dimension_name, weight, description) VALUES
('Referential Integrity', 'Referential Integrity', 0.20, 'Consistency and existence of foreign key relationships across entities'),
('Financial', 'Financial Integrity', 0.20, 'Mathematical accuracy of billing, payments, adjustments, and reconciliations'),
('Completeness', 'Completeness', 0.15, 'Presence of all mandatory attributes and itemized lines'),
('Validity', 'Validity', 0.15, 'Conformance of identifiers and codes to syntax and standards (NPI, CPT, ICD-10)'),
('Uniqueness', 'Uniqueness', 0.10, 'Absence of duplicate claims or payments'),
('Temporal', 'Temporal Consistency', 0.10, 'Chronological plausibility of service, submission, and payment dates'),
('Accuracy', 'Accuracy / Consistency', 0.10, 'Business logic alignment between statuses, charges, and actions')
ON DUPLICATE KEY UPDATE weight = VALUES(weight);

-- Reference Root Causes
INSERT INTO ref_root_causes (root_cause_code, root_cause_name, description) VALUES
('DATA_ENTRY_ERROR', 'Data Entry Error', 'Typo or formatting error in charge capture or intake'),
('SYSTEM_CONFIG_ERROR', 'System Configuration Bug', 'EHR or billing software mapping mismatch'),
('PAYER_ADJUDICATION_DEFECT', 'Payer Adjudication Defect', 'Payer processed claim contrary to contracted fee schedule'),
('TIMING_DESYNCHRONIZATION', 'Timing Desynchronization', 'Transactions arrived or processed out of chronological sequence'),
('DUPLICATE_SUBMISSION', 'Duplicate Submission', 'Repeat electronic submission without replacement frequency code'),
('REFERENTIAL_MISSING_MASTER', 'Missing Master Record', 'Feed missing provider, facility, or patient master entry'),
('CALCULATION_ROUNDING_DEFECT', 'Calculation Rounding Error', 'Fractional cent rounding divergence between lines and total')
ON DUPLICATE KEY UPDATE root_cause_name = VALUES(root_cause_name);

-- Reference Adjustment Group Codes
INSERT INTO ref_adjustment_group_codes (group_code, group_name, description) VALUES
('CO', 'Contractual Obligation', 'Contractual reduction between billed charge and allowed fee schedule'),
('PR', 'Patient Responsibility', 'Deductible, copayment, or coinsurance owed by the patient'),
('OA', 'Other Adjustment', 'Mandatory adjustment not covered by other categories'),
('PI', 'Payer Initiated Reduction', 'Reduction initiated by payer due to medical policy'),
('CR', 'Correction and Reversal', 'Prior payment or adjustment reversal')
ON DUPLICATE KEY UPDATE group_name = VALUES(group_name);

-- QA Rule Categories
INSERT INTO qa_rule_categories (category_id, category_code, category_name, description) VALUES
(1, 'COMPLETENESS', 'Data Completeness Rules', 'Rules verifying required attributes are not null or empty'),
(2, 'VALIDITY', 'Format & Syntax Validity', 'Rules verifying NPI Luhn checks, CPT and ICD-10 code formats'),
(3, 'UNIQUENESS', 'Uniqueness & Duplicate Detection', 'Rules identifying duplicate claims and double payments'),
(4, 'FINANCIAL', 'Financial & Reconciliation Rules', 'Rules auditing overpayments, negative values, and balances'),
(5, 'TEMPORAL', 'Temporal & Chronological Rules', 'Rules auditing date ordering and timely filing limits'),
(6, 'REFERENTIAL', 'Referential Integrity Rules', 'Rules detecting orphaned claims, lines, and transactions'),
(7, 'BUSINESS_LOGIC', 'Business Logic & State Rules', 'Rules auditing claim status and payment consistency')
ON DUPLICATE KEY UPDATE category_name = VALUES(category_name);

SET FOREIGN_KEY_CHECKS = 1;

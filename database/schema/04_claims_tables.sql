-- ============================================================================
-- ClaimIQ Database Schema: 04_claims_tables.sql
-- Database Engine: MySQL 8.x (InnoDB)
-- Character Set: utf8mb4 / utf8mb4_0900_ai_ci
-- ============================================================================

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

-- ============================================================================
-- ClaimIQ Database Schema: 05_financial_tables.sql
-- Database Engine: MySQL 8.x (InnoDB)
-- Character Set: utf8mb4 / utf8mb4_0900_ai_ci
-- ============================================================================

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

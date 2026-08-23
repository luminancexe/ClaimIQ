-- ============================================================================
-- ClaimIQ Database Schema: 10_ground_truth_tables.sql
-- Database Engine: MySQL 8.x (InnoDB)
-- Character Set: utf8mb4 / utf8mb4_0900_ai_ci
-- Phase: 4 — Controlled Error Injection & Anomaly Dataset Engineering
-- ============================================================================

CREATE TABLE IF NOT EXISTS anomaly_ground_truth (
    ground_truth_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    anomaly_code VARCHAR(16) NOT NULL,
    category_name VARCHAR(64) NOT NULL,
    severity_code VARCHAR(16) NOT NULL,
    target_table VARCHAR(64) NOT NULL,
    target_record_id BIGINT UNSIGNED NOT NULL,
    target_business_reference VARCHAR(64) NULL,
    target_column VARCHAR(64) NOT NULL,
    original_value TEXT NULL,
    mutated_value TEXT NULL,
    injection_profile VARCHAR(32) NOT NULL,
    injection_seed INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    expected_rule_category VARCHAR(64) NOT NULL,
    injected_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    CONSTRAINT pk_anomaly_ground_truth PRIMARY KEY (ground_truth_id),
    CONSTRAINT fk_agt_severity FOREIGN KEY (severity_code) REFERENCES ref_severities (severity_code) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Secondary indexes for efficient Phase 4 reset and Phase 5 QA reconciliation
CREATE INDEX idx_agt_code ON anomaly_ground_truth (anomaly_code);
CREATE INDEX idx_agt_target ON anomaly_ground_truth (target_table, target_record_id);
CREATE INDEX idx_agt_profile ON anomaly_ground_truth (injection_profile, is_active);
CREATE INDEX idx_agt_injected_at ON anomaly_ground_truth (injected_at);

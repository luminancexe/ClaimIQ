-- ============================================================================
-- ClaimIQ Database Schema: 01_reference_tables.sql
-- Database Engine: MySQL 8.x (InnoDB)
-- Character Set: utf8mb4 / utf8mb4_0900_ai_ci
-- ============================================================================

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

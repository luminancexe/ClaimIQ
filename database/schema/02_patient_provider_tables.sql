-- ============================================================================
-- ClaimIQ Database Schema: 02_patient_provider_tables.sql
-- Database Engine: MySQL 8.x (InnoDB)
-- Character Set: utf8mb4 / utf8mb4_0900_ai_ci
-- ============================================================================

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

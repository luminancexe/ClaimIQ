-- ============================================================================
-- ClaimIQ Database Schema: 03_clinical_encounter_tables.sql
-- Database Engine: MySQL 8.x (InnoDB)
-- Character Set: utf8mb4 / utf8mb4_0900_ai_ci
-- ============================================================================

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

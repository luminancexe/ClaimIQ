-- ============================================================================
-- ClaimIQ Database Schema: 07_audit_tables.sql
-- Database Engine: MySQL 8.x (InnoDB)
-- Character Set: utf8mb4 / utf8mb4_0900_ai_ci
-- ============================================================================

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

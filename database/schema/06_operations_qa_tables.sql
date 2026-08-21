-- ============================================================================
-- ClaimIQ Database Schema: 06_operations_qa_tables.sql
-- Database Engine: MySQL 8.x (InnoDB)
-- Character Set: utf8mb4 / utf8mb4_0900_ai_ci
-- ============================================================================

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

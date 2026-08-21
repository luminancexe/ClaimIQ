-- ============================================================================
-- ClaimIQ Database Schema: 08_indexes.sql
-- Database Engine: MySQL 8.x (InnoDB B-Tree Secondary Indexes)
-- ============================================================================

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

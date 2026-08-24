# ClaimIQ — Requirements Traceability Matrix (RTM)

## 1. Priority Model & Governance

ClaimIQ uses a four-level priority classification to govern implementation phases:

- **P0 (Essential / MVP Core)**: Non-negotiable foundational requirements necessary for core data operations, SQL QA validation, and data integrity.
- **P1 (Important / Core Operations)**: High-priority capabilities required for complete analyst workflow, issue lifecycle management, and standard reporting.
- **P2 (Enhancement / Advanced Operations)**: Advanced features that improve operational efficiency, provider/payer scorecards, and batch management.
- **P3 (Optional / Future Innovation)**: Advanced integrations such as AI-assisted root-cause explanations and extended file export options.

---

## 2. Comprehensive Traceability Matrix (Updated for Phase 4: Error Injection & Anomaly Datasets)

| Requirement ID | Requirement Summary | Category | Priority | Target Phase | Implementation Module / Entity | Column(s) & Constraints (MySQL 8.x) | Validation Method | Current Status |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :---: |
| **FR-DM-001** | Store synthetic patient master records | Data Mgmt | **P0** | Phase 2/3 | `generator/generators/patients.py` | `patient_id` (PK), `patient_reference` (UQ), `first_name`, `last_name`, `date_of_birth` | Unit Test & SQL Validation | **Implemented** |
| **FR-DM-002** | Store synthetic provider records with NPI | Data Mgmt | **P0** | Phase 2/3 | `generator/generators/providers.py` | `provider_id` (PK), `npi` (UQ 10-digit), `facility_id` (FK), `specialty` | Luhn Unit Test & SQL Audit | **Implemented** |
| **FR-DM-003** | Store synthetic healthcare facility records | Data Mgmt | **P0** | Phase 2/3 | `generator/generators/facilities.py` | `facility_id` (PK), `facility_reference` (UQ), `facility_name`, `tin` | Unit Test & SQL Validation | **Implemented** |
| **FR-DM-004** | Store synthetic payer records with filing limits | Data Mgmt | **P0** | Phase 2/3 | `generator/generators/payers.py` | `payer_id` (PK), `timely_filing_days`, `plan_id` (FK) | Unit Test & SQL Validation | **Implemented** |
| **FR-DM-005** | Store synthetic clinical encounter records | Data Mgmt | **P0** | Phase 2/3 | `generator/generators/encounters.py` | `encounter_id` (PK), `patient_id` (FK), `provider_id` (FK), `date_of_service` | Chronology Test & SQL Audit | **Implemented** |
| **FR-DM-006** | Support batch ingestion of synthetic datasets | Data Mgmt | **P0** | Phase 3 | `generator/database.py` (`bulk_insert`) | Parameterized `executemany` chunking (2,500 rows) | Scale Benchmark Test | **Implemented** |
| **FR-DM-007** | Strict synthetic data isolation (Zero PHI) | Data Mgmt | **P0** | Phase 3/4 | All generator & injector modules | Synthetic identifier schemas (`PAT-`, `CLM-`, `PRV-`) | Automated Validation Suite | **Implemented** |
| **FR-QA-001** | Execute automated SQL data quality rules | QA Engine | **P0** | Phase 5 | `qa/engine.py`, `qa/rules/` | `qa_rules.sql_logic`, `qa_results` | Automated SQL QA Suite | **Implemented** |
| **FR-QA-002** | Categorize rules across 7 DQ dimensions | QA Engine | **P0** | Phase 5 | `qa/scoring.py`, `qa_rules` | `dimension_code` (FK `ref_dq_dimensions`) | Rule Metadata Verification | **Implemented** |
| **FR-QA-003** | Assign default severity levels (Critical–Low) | QA Engine | **P0** | Phase 5 | `qa/registry.py`, `qa_rules` | `default_severity_code` (FK `ref_severities`) | Rule Schema Test | **Implemented** |
| **FR-QA-004** | Detect duplicate claims on identical DOS/CPT | QA Engine | **P0** | Phase 4/5 | `qa/rules/duplication.py` (`R-E011`–`R-E015`) | `claims`, `claim_lines`, `anomaly_ground_truth` | Anomaly Test & Ground Truth Audit | **Implemented** |
| **FR-QA-005** | Detect missing mandatory fields | QA Engine | **P0** | Phase 4/5 | `qa/rules/completeness.py` (`R-E001`–`R-E010`) | `anomaly_ground_truth`, all core tables | Completeness Mutation Test | **Implemented** |
| **FR-QA-006** | Verify format validity (NPI Luhn, CPT, ICD-10) | QA Engine | **P0** | Phase 3/4/5 | `qa/rules/formatting.py` (`R-E061`–`R-E067`) | `npi`, `cpt_code`, `icd10_code`, `taxonomy_code` | Format Mutation & Unit Test | **Implemented** |
| **FR-QA-007** | Flag temporal sequence violations | QA Engine | **P0** | Phase 3/4/5 | `qa/rules/temporal.py` (`R-E034`–`R-E042`) | `date_of_service`, `submission_date`, `payment_date` | Chronology Mutation Test | **Implemented** |
| **FR-QA-008** | Detect orphaned records and referential breaks | QA Engine | **P0** | Phase 3/4/5 | `qa/rules/referential.py` (`R-E016`–`R-E022`) | `providers`, `claims`, `payments`, `remittances` | Cross-Entity Mutation Test | **Implemented** |
| **FR-QA-009** | Compute aggregate Data Quality (DQ) Score | QA Engine | **P0** | Phase 5/6 | `qa/scoring.py` (`calculate_dq_score`) | `dq_score` (DECIMAL(5, 2)), `ref_dq_dimensions.weight` | Formula Unit Test | **Implemented** |
| **FR-QA-010** | Support manual and scheduled batch execution | QA Engine | **P1** | Phase 5 | `qa/cli.py` (`python -m qa --run`) | `run_id` (PK), `run_reference` (UQ), `batch_identifier`, `started_at` | CLI Runner Test | **Implemented** |
| **FR-QA-011** | Log rule execution telemetry and latency | QA Engine | **P1** | Phase 5 | `qa/engine.py`, `qa_results` | `execution_duration_ms`, `records_evaluated`, `issues_detected` | Execution Telemetry Test | **Implemented** |
| **FR-CLM-001** | Store claim header records with status | Claims | **P0** | Phase 2/3 | `generator/generators/claims.py` | `claim_id` (PK), `claim_reference` (UQ), `current_status_code` (FK), `total_billed_amount` | Pipeline Insert & SQL Audit | **Implemented** |
| **FR-CLM-002** | Store itemized claim line records | Claims | **P0** | Phase 2/3 | `generator/generators/claim_lines.py` | `claim_line_id` (PK), `claim_id` (FK), `units`, `unit_price`, `line_billed_amount` | Itemization Math Audit | **Implemented** |
| **FR-CLM-003** | Multi-attribute claims search and filtering | Claims | **P1** | Phase 7/8 | `claims` | `idx_claims_status_sub`, `idx_claims_pat`, `idx_claims_prov`, `idx_claims_payer` | API & UI Integration Test | Schema Ready |
| **FR-CLM-004** | Comprehensive claim detail view | Claims | **P1** | Phase 8 | `claims`, `claim_lines`, `claim_status_history` | Normalized 1:N relations to lines, payments, adjustments, and issues | UI Component Test | Schema Ready |
| **FR-CLM-005** | Validate header billed sum equals line sums | Claims | **P0** | Phase 3/4/5 | `qa/rules/financial.py` (`R-E030`) | `claims.total_billed_amount`, `claim_lines.line_billed_amount` | Financial Mutation Test | **Implemented** |
| **FR-ANL-001** | Store payment transaction records | Analytics | **P0** | Phase 2/3 | `generator/generators/payments.py` | `payment_id` (PK), `remittance_id` (FK), `claim_id` (FK), `paid_amount` (DECIMAL(12,2)) | Batch Allocation & Audit | **Implemented** |
| **FR-ANL-002** | Store adjustment and denial records | Analytics | **P0** | Phase 2/3 | `generator/generators/adjustments.py` | `adjustment_id` (PK), `group_code` (FK `ref_adjustment_group_codes`), `denial_code` | Adjustment Sum Audit | **Implemented** |
| **FR-ANL-003** | Detect overpayments (Paid $>$ Billed) | Analytics | **P0** | Phase 3/4/5 | `qa/rules/financial.py` (`R-E023`, `R-E028`) | `claims.total_billed_amount`, `payments.paid_amount` | Overpayment Mutation Test | **Implemented** |
| **FR-ANL-004** | Detect negative monetary values | Analytics | **P0** | Phase 2/3 | All financial tables | MySQL 8.x `CHECK (... >= 0.00)` constraints | Negative Value Guard | **Implemented** |
| **FR-ANL-005** | Detect reconciliation equation discrepancies | Analytics | **P0** | Phase 3/4/5 | `qa/rules/financial.py` (`R-E029`) | `reconciliation_id` (PK), `variance_amount`, `reconciliation_status` | Variance Mutation Test | **Implemented** |
| **FR-ANL-006** | Detect duplicate payment transactions | Analytics | **P0** | Phase 3/4/5 | `qa/rules/duplication.py` (`R-E013`) | `remittances.check_trace_number` (UQ), `payments.payment_reference` (UQ) | Duplicate Payment Test | **Implemented** |
| **FR-ANL-007** | Aggregate total financial variance at risk | Analytics | **P1** | Phase 6 | `reconciliations`, `issues` | `issues.variance_amount`, `reconciliations.variance_amount` | Financial Rollup Test | Schema Ready |
| **FR-ISS-001** | Automatically generate unique issue records | Issues | **P0** | Phase 5 | `qa/database.py` (`save_detected_issues`) | `issue_id` (PK), `issue_reference` (UQ), `rule_id` (FK), `claim_id` (FK) | Engine Generation Test | **Implemented** |
| **FR-ISS-002** | Enforce issue lifecycle state machine | Issues | **P0** | Phase 7/9 | `ref_issue_statuses`, `issue_history` | `current_status_code` (FK), `issue_history.previous_status_code` (FK) | FSM State Transition Test | **Implemented** |
| **FR-ISS-003** | Enforce user assignment before investigation | Issues | **P1** | Phase 7/9 | `issues` | `assigned_to_user` (VARCHAR 100) | Validation Rule & API Test | Schema Ready |
| **FR-ISS-004** | Provide Issue Investigation Workbench UI | Issues | **P0** | Phase 9 | `issues`, `issue_notes`, `issue_history` | Full relational schema for investigation metadata | UI E2E Test | Schema Ready |
| **FR-ISS-005** | Require root-cause category upon resolution | Issues | **P0** | Phase 7/9 | `issues`, `ref_root_causes` | `root_cause_code` (FK `ref_root_causes`) | Mandatory Field Test | **Implemented** |
| **FR-ISS-006** | Require justification notes for resolutions | Issues | **P0** | Phase 7/9 | `issue_history`, `issue_notes` | `issue_history.transition_notes` (TEXT), `issue_notes.note_text` (TEXT) | Mandatory Field Test | Schema Ready |
| **FR-ISS-007** | Support user and team assignment | Issues | **P1** | Phase 7/9 | `issues` | `assigned_to_user`, `idx_issues_assigned` | Assignment API Test | Schema Ready |
| **FR-ISS-008** | Support bulk triage and status updates | Issues | **P2** | Phase 9 | `issues` | `idx_issues_status_sev` compound index | Bulk Action Test | Schema Ready |
| **FR-REP-001** | Generate Daily Data Quality Report | Reporting | **P0** | Phase 6/8 | `qa_execution_runs`, `issues` | `qa_execution_runs.dq_score`, `issues.severity_code` | Report Output Test | Schema Ready |
| **FR-REP-002** | Generate Weekly Operations & SLA Report | Reporting | **P1** | Phase 6/8 | `issues`, `ref_severities` | `ref_severities.sla_hours`, `issues.detected_at`, `issues.resolved_at` | Metrics Rollup Test | Schema Ready |
| **FR-REP-003** | Generate Provider Quality Scorecard | Reporting | **P1** | Phase 6/8 | `providers`, `claims`, `issues` | `claims.billing_provider_id`, `idx_claims_prov` | Provider Aggregation Test | Schema Ready |
| **FR-REP-004** | Generate Payer Adjudication Report | Reporting | **P1** | Phase 6/8 | `payers`, `claims`, `denials` | `claims.payer_id`, `idx_claims_payer`, `denials.denial_code` | Payer Aggregation Test | Schema Ready |
| **FR-REP-005** | Generate Financial Discrepancy Ledger | Reporting | **P0** | Phase 6/8 | `reconciliations`, `issues` | `reconciliations.variance_amount`, `issues.variance_amount` | Ledger Export Test | Schema Ready |
| **FR-REP-006** | Support export to CSV, PDF, and JSON | Reporting | **P1** | Phase 9 | All reporting views | Structured relational query support | File Stream Test | Planned (Phase 9) |
| **FR-DOC-001** | Maintain centralized QA Rules Knowledge Base | Documentation| **P1** | Phase 10 | `qa_rules`, `qa_rule_categories` | `qa_rules.description`, `qa_rules.sql_logic` | Content & UI Test | Schema Ready |
| **FR-DOC-002** | Document rule SQL logic and remediation SOPs | Documentation| **P1** | Phase 10 | `qa_rules` | `qa_rules.sql_logic`, `qa_rules.description` | Knowledge Base Audit | Schema Ready |
| **FR-DOC-003** | Deep-link issues directly to rule documentation | Documentation| **P1** | Phase 9/10 | `issues`, `qa_rules` | `issues.rule_id` (FK `qa_rules.rule_id`) | Deep-Link Navigation Test | Schema Ready |
| **FR-DOC-004** | Version control for rule definitions | Documentation| **P2** | Phase 10 | `qa_rules` | `qa_rules.updated_at` (DATETIME(6)) | History Tracking Test | Schema Ready |
| **FR-USR-001** | Support 5 predefined user roles | Users/RBAC | **P0** | Phase 7 | Backend / App Layer | Mapped in Phase 1 `docs/users-and-roles.md` | RBAC Authorization Test | Planned (Phase 7) |
| **FR-USR-002** | Enforce RBAC permission matrix | Users/RBAC | **P0** | Phase 7 | Backend / App Layer | RBAC role checks on API routes | Security Permission Test | Planned (Phase 7) |
| **FR-USR-003** | Restrict raw data mutations for non-admins | Users/RBAC | **P0** | Phase 7 | Database Permissions | MySQL user privileges (`GRANT SELECT, INSERT, UPDATE`) | Security Boundary Test | Planned (Phase 7) |
| **FR-USR-004** | Enforce secure credentials and sessions | Users/RBAC | **P1** | Phase 7/11 | Backend / App Layer | Password hashing and JWT tokens | Auth Security Test | Planned (Phase 7) |
| **FR-AI-001** | Generate AI-assisted issue explanations | AI Operations | **P3** | Phase 12 | `issues`, `qa_rules` | Relational issue context extraction | LLM Prompt & Output Test | Planned (Phase 12) |
| **FR-AI-002** | Restrict AI prompts to verified SQL context | AI Operations | **P3** | Phase 12 | `issues`, `qa_rules`, `claims` | Relational context snapshot extraction | Context Isolation Test | Planned (Phase 12) |
| **FR-AI-003** | Output structured root-cause recommendations | AI Operations | **P3** | Phase 12 | `issues.root_cause_code` | Mapped to `ref_root_causes` | Schema Validation Test | Planned (Phase 12) |
| **FR-AI-004** | Display advisory disclaimers on AI output | AI Operations | **P3** | Phase 12 | UI Layer | UI disclaimer component | UI Verification | Planned (Phase 12) |
| **FR-AI-005** | One-click copy AI findings into notes thread | AI Operations | **P3** | Phase 12 | `issue_notes` | `note_text` (TEXT) | UI Interaction Test | Planned (Phase 12) |
| **FR-AUD-001** | Append-only immutable audit logging | Auditability | **P0** | Phase 2/7 | `audit_events` | `audit_id` (PK), `event_timestamp` (DATETIME(6)), `actor_user`, `action_type` | Audit Immutability Test | **Implemented** |
| **FR-AUD-002** | Capture full state before and after change | Auditability | **P0** | Phase 2/7 | `audit_events` | `previous_state_json` (JSON), `new_state_json` (JSON) | JSON Diff Verification | **Implemented** |
| **FR-AUD-003** | Prevent deletion or truncation of audit logs | Auditability | **P0** | Phase 2/11 | `audit_events` | MySQL Table Privileges (Disallow `DELETE` / `TRUNCATE`) | DB Permission & Trigger | **Implemented** |
| **FR-AUD-004** | Audit Trail Explorer with search and filter | Auditability | **P1** | Phase 8/9 | `audit_events` | `idx_audit_entity`, `idx_audit_actor_ts` | Audit UI Explorer Test | Schema Ready |

---

## 3. Non-Functional Requirements Traceability (Phase 4 Error Injection)

| Requirement ID | Summary | Category | Priority | Target Phase | Implementation Mechanism | Validation Method | Status |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: |
| **NFR-DI-001** | Deterministic error injection ($100\%$) | Data Integrity | **P0** | Phase 4 | Centralized `GeneratorRandomState(seed)` | Seed 42 Repeatability Test | **Implemented** |
| **NFR-DI-002** | ACID transaction compliance | Data Integrity | **P0** | Phase 2/4 | Atomic mutation commits & rollback on failure | Transaction Rollback Test | **Implemented** |
| **NFR-DI-003** | Clean baseline reversibility | Data Integrity | **P0** | Phase 4 | Two-way reversion engine (`--reset-anomalies`) | Post-Reset Phase 3 Audit | **Implemented** |
| **NFR-PRF-001** | High throughput mutation execution | Performance | **P0** | Phase 4 | Batch parameterized mutation updates | Profile Injection Benchmarks | **Implemented** |
| **NFR-SEC-001** | Zero PHI containment enforcement | Security | **P0** | Phase 3/4 | Fictional synthetic mutations; zero real PHI | Synthetic Audit Verification | **Implemented** |
| **NFR-REL-002** | Safe database reset and reproducibility | Reliability | **P0** | Phase 3/4 | Dependency-safe reset + ground truth restoration | Reset & Re-injection Test | **Implemented** |

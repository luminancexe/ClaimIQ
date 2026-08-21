-- ============================================================================
-- ClaimIQ Database Schema: 09_seed_reference_data.sql
-- Database Engine: MySQL 8.x
-- Description: Controlled seed/reference values for reference tables
-- ============================================================================

-- 1. Reference Claim Statuses
INSERT INTO ref_claim_statuses (status_code, status_name, description, is_terminal) VALUES
('Submitted', 'Submitted', 'Claim electronically transmitted to payer/clearinghouse', 0),
('Accepted', 'Accepted', 'Claim passed front-end EDI validation and pre-adjudication edits', 0),
('Rejected', 'Rejected', 'Claim failed front-end EDI validation before adjudication', 0),
('Pending', 'Pending Review', 'Claim undergoing medical review or awaiting documentation', 0),
('Denied', 'Denied', 'Claim adjudicated and formally refused reimbursement', 1),
('Paid', 'Paid in Full', 'Claim adjudicated and fully paid per fee schedule', 1),
('Partially Paid', 'Partially Paid', 'Claim adjudicated with partial payment and contractual adjustment', 1)
ON DUPLICATE KEY UPDATE status_name = VALUES(status_name);

-- 2. Reference Issue Statuses
INSERT INTO ref_issue_statuses (status_code, status_name, description, is_terminal) VALUES
('Detected', 'Detected', 'Anomaly identified by QA engine pending triage', 0),
('Open', 'Open', 'Issue queued in operational worklist awaiting assignment', 0),
('Investigating', 'In Investigation', 'Analyst actively inspecting root cause and context', 0),
('Resolved', 'Resolved', 'Defect verified and reconciled with root-cause documentation', 1),
('False Positive', 'False Positive', 'Investigated and confirmed as legitimate edge case', 1),
('Escalated', 'Escalated', 'Systemic bug or external payer issue requiring leadership', 0),
('Ignored', 'Ignored / Suppressed', 'Accepted non-blocking technical debt with manager approval', 1)
ON DUPLICATE KEY UPDATE status_name = VALUES(status_name);

-- 3. Reference Severities
INSERT INTO ref_severities (severity_code, severity_name, sla_hours, priority_rank) VALUES
('Critical', 'Critical Severity', 4, 1),
('High', 'High Severity', 24, 2),
('Medium', 'Medium Severity', 72, 3),
('Low', 'Low Severity', 168, 4)
ON DUPLICATE KEY UPDATE sla_hours = VALUES(sla_hours);

-- 4. Reference Data Quality Dimensions
INSERT INTO ref_dq_dimensions (dimension_code, dimension_name, weight, description) VALUES
('Referential Integrity', 'Referential Integrity', 0.20, 'Consistency and existence of foreign key relationships across entities'),
('Financial', 'Financial Integrity', 0.20, 'Mathematical accuracy of billing, payments, adjustments, and reconciliations'),
('Completeness', 'Completeness', 0.15, 'Presence of all mandatory attributes and itemized lines'),
('Validity', 'Validity', 0.15, 'Conformance of identifiers and codes to syntax and standards (NPI, CPT, ICD-10)'),
('Uniqueness', 'Uniqueness', 0.10, 'Absence of duplicate claims or payments'),
('Temporal', 'Temporal Consistency', 0.10, 'Chronological plausibility of service, submission, and payment dates'),
('Accuracy', 'Accuracy / Consistency', 0.10, 'Business logic alignment between statuses, charges, and actions')
ON DUPLICATE KEY UPDATE weight = VALUES(weight);

-- 5. Reference Root Causes
INSERT INTO ref_root_causes (root_cause_code, root_cause_name, description) VALUES
('DATA_ENTRY_ERROR', 'Data Entry Error', 'Typo or formatting error in charge capture or intake'),
('SYSTEM_CONFIG_ERROR', 'System Configuration Bug', 'EHR or billing software mapping mismatch'),
('PAYER_ADJUDICATION_DEFECT', 'Payer Adjudication Defect', 'Payer processed claim contrary to contracted fee schedule'),
('TIMING_DESYNCHRONIZATION', 'Timing Desynchronization', 'Transactions arrived or processed out of chronological sequence'),
('DUPLICATE_SUBMISSION', 'Duplicate Submission', 'Repeat electronic submission without replacement frequency code'),
('REFERENTIAL_MISSING_MASTER', 'Missing Master Record', 'Feed missing provider, facility, or patient master entry'),
('CALCULATION_ROUNDING_DEFECT', 'Calculation Rounding Error', 'Fractional cent rounding divergence between lines and total')
ON DUPLICATE KEY UPDATE root_cause_name = VALUES(root_cause_name);

-- 6. Reference Adjustment Group Codes
INSERT INTO ref_adjustment_group_codes (group_code, group_name, description) VALUES
('CO', 'Contractual Obligation', 'Contractual reduction between billed charge and allowed fee schedule'),
('PR', 'Patient Responsibility', 'Deductible, copayment, or coinsurance owed by the patient'),
('OA', 'Other Adjustment', 'Mandatory adjustment not covered by other categories'),
('PI', 'Payer Initiated Reduction', 'Reduction initiated by payer due to medical policy'),
('CR', 'Correction and Reversal', 'Prior payment or adjustment reversal')
ON DUPLICATE KEY UPDATE group_name = VALUES(group_name);

-- 7. QA Rule Categories
INSERT INTO qa_rule_categories (category_id, category_code, category_name, description) VALUES
(1, 'COMPLETENESS', 'Data Completeness Rules', 'Rules verifying required attributes are not null or empty'),
(2, 'VALIDITY', 'Format & Syntax Validity', 'Rules verifying NPI Luhn checks, CPT and ICD-10 code formats'),
(3, 'UNIQUENESS', 'Uniqueness & Duplicate Detection', 'Rules identifying duplicate claims and double payments'),
(4, 'FINANCIAL', 'Financial & Reconciliation Rules', 'Rules auditing overpayments, negative values, and balances'),
(5, 'TEMPORAL', 'Temporal & Chronological Rules', 'Rules auditing date ordering and timely filing limits'),
(6, 'REFERENTIAL', 'Referential Integrity Rules', 'Rules detecting orphaned claims, lines, and transactions'),
(7, 'BUSINESS_LOGIC', 'Business Logic & State Rules', 'Rules auditing claim status and payment consistency')
ON DUPLICATE KEY UPDATE category_name = VALUES(category_name);

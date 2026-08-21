# ClaimIQ — Functional Requirements Specification

## 1. Requirement Taxonomy & Organization

The functional requirements for ClaimIQ are grouped into ten domain areas:
1. **Data Management & Ingestion (`FR-DM`)**
2. **QA Rules & Validation Engine (`FR-QA`)**
3. **Claims Management & Exploration (`FR-CLM`)**
4. **Analytics & Financial Integrity (`FR-ANL`)**
5. **Issue Tracking & Investigation (`FR-ISS`)**
6. **Operational Reporting & Exports (`FR-REP`)**
7. **Rules Documentation & SOPs (`FR-DOC`)**
8. **User Management & Access Control (`FR-USR`)**
9. **AI-Assisted Operations & Root Cause (`FR-AI`)**
10. **Auditability, Traceability & Logging (`FR-AUD`)**

---

## 2. Functional Requirements by Domain

### 2.1 Data Management & Ingestion (`FR-DM`)

- **FR-DM-001**: The system shall store synthetic patient master records, including unique patient identifier, demographic attributes, and synthetic insurance policy details.
- **FR-DM-002**: The system shall store synthetic healthcare provider records, including unique provider identifier, 10-digit National Provider Identifier (NPI), medical specialty, and taxonomy code.
- **FR-DM-003**: The system shall store synthetic healthcare facility and organization records, including facility identifier, organization name, and billing tax identification number (TIN).
- **FR-DM-004**: The system shall store synthetic payer records, including payer identifier, payer name, plan type (e.g., Commercial, Medicare, Medicaid), and timely filing threshold (days).
- **FR-DM-005**: The system shall store synthetic clinical encounter records linking patients and providers with a date of service (DOS), encounter type, and service facility.
- **FR-DM-006**: The system shall support batch ingestion of synthetic claims data via structured CSV, JSON, or SQL seed scripts.
- **FR-DM-007**: The system shall isolate all data storage within synthetic environments, enforcing zero persistence or exposure of real Protected Health Information (PHI).

---

### 2.2 QA Rules & Validation Engine (`FR-QA`)

- **FR-QA-001**: The system shall execute automated SQL-based data quality validation rules across ingested datasets.
- **FR-QA-002**: The system shall categorize every QA rule under one of the 7 core Data Quality Dimensions: Accuracy, Completeness, Consistency, Validity, Uniqueness, Timeliness, or Referential Integrity.
- **FR-QA-003**: The system shall assign a default severity level (`Critical`, `High`, `Medium`, `Low`) to every QA rule.
- **FR-QA-004**: The system shall execute Uniqueness rules to detect duplicate claims sharing identical patient, provider, date of service, procedure code, and billed charge.
- **FR-QA-005**: The system shall execute Completeness rules to detect missing or null values in mandatory fields (e.g., `patient_id`, `provider_npi`, `diagnosis_code`, `date_of_service`).
- **FR-QA-006**: The system shall execute Validity rules to verify format compliance (e.g., 10-digit Luhn-valid NPIs, valid 5-digit CPT syntax, valid alphanumeric ICD-10 format).
- **FR-QA-007**: The system shall execute Temporal rules to flag chronological anomalies (e.g., Submission Date $<$ Date of Service, Payment Date $<$ Submission Date, Future Dates).
- **FR-QA-008**: The system shall execute Referential Integrity rules to detect orphaned records (e.g., claims missing patient/provider/payer foreign keys, payments missing claim references).
- **FR-QA-009**: The system shall compute an aggregate Data Quality (DQ) Score (0.0% – 100.0%) for each batch execution based on a weighted scoring formula.
- **FR-QA-010**: The system shall support on-demand manual execution and scheduled batch execution of the QA engine.
- **FR-QA-011**: The system shall log execution telemetry for each rule run, including start timestamp, completion timestamp, rows evaluated, failure count, and execution latency.

---

### 2.3 Claims Management & Exploration (`FR-CLM`)

- **FR-CLM-001**: The system shall store claim header records containing `claim_id`, `encounter_id`, `patient_id`, `provider_id`, `payer_id`, `submission_date`, `claim_status`, and `total_billed_amount`.
- **FR-CLM-002**: The system shall store itemized claim line records containing `line_id`, `claim_id`, `line_number`, `cpt_code`, `units`, `unit_price`, and `line_billed_amount`.
- **FR-CLM-003**: The system shall provide a multi-attribute Claims Search and Filter interface supporting search by Claim ID, Patient ID, Provider NPI, Payer ID, Status, and Date Range.
- **FR-CLM-004**: The system shall provide a comprehensive Claim Detail View rendering the claim header, line items, associated patient/provider details, linked payments, and any active QA issues.
- **FR-CLM-005**: The system shall validate that the header `total_billed_amount` strictly equals the arithmetic sum of child `line_billed_amount` values.

---

### 2.4 Analytics & Financial Integrity (`FR-ANL`)

- **FR-ANL-001**: The system shall store payment transaction records containing `payment_id`, `claim_id`, `paid_amount`, `payment_date`, `payment_method`, and `remittance_trace_number`.
- **FR-ANL-002**: The system shall store contractual adjustment and denial records containing `adjustment_id`, `claim_id`, `group_code` (e.g., `CO`, `PR`), `reason_code` (CARC), and `amount`.
- **FR-ANL-003**: The system shall detect financial overpayments where `paid_amount > total_billed_amount`.
- **FR-ANL-004**: The system shall detect negative monetary values in billed, paid, or adjustment amounts unless explicitly flagged as reversing transactions.
- **FR-ANL-005**: The system shall detect reconciliation discrepancies where:
  $$\left|\text{Billed Amount} - (\text{Paid Amount} + \text{Adjustment Amount} + \text{Patient Responsibility})\right| > \$0.01$$
- **FR-ANL-006**: The system shall detect duplicate payment transactions sharing the same remittance trace number or check identifier.
- **FR-ANL-007**: The system shall aggregate total financial variance and at-risk dollar amounts across all detected financial discrepancies.

---

### 2.5 Issue Tracking & Investigation (`FR-ISS`)

- **FR-ISS-001**: The system shall automatically generate a unique issue record (`ISS-XXXXXX`) whenever a QA rule detects a data anomaly.
- **FR-ISS-002**: The system shall maintain an Issue Lifecycle state machine supporting statuses: `Detected`, `Open`, `Investigating`, `Resolved`, `False Positive`, `Escalated`, and `Ignored`.
- **FR-ISS-003**: The system shall enforce mandatory analyst assignment before transitioning an issue from `Open` to `Investigating`.
- **FR-ISS-004**: The system shall provide an Issue Investigation Workbench displaying the triggering rule, failed SQL query, affected records, historical claim timeline, and investigation notes.
- **FR-ISS-005**: The system shall require mandatory root-cause categorization (e.g., `Data Entry Error`, `Vendor Mapping Flaw`, `Payer Adjudication Bug`, `Timing Desynchronization`) upon issue resolution.
- **FR-ISS-006**: The system shall require mandatory justification notes when marking an issue as `Resolved` or `False Positive`.
- **FR-ISS-007**: The system shall support assigning issues to specific users or teams and reassigning open issues.
- **FR-ISS-008**: The system shall support bulk status updates and bulk assignments for low-severity issues.

---

### 2.6 Operational Reporting & Exports (`FR-REP`)

- **FR-REP-001**: The system shall generate a Daily Data Quality Report summarizing batch execution results, DQ score, total records processed, new issues detected, and open critical defects.
- **FR-REP-002**: The system shall generate a Weekly Operations Report tracking issue resolution velocity, Mean Time to Resolution (MTTR), SLA compliance, and backlog aging.
- **FR-REP-003**: The system shall generate a Provider Quality Scorecard ranking providers by error rate, missing data frequency, and billing discrepancy volume.
- **FR-REP-004**: The system shall generate a Payer Adjudication & Error Report tracking denial rates, adjustment ratios, and payment timing variances by payer.
- **FR-REP-005**: The system shall generate a Financial Discrepancy Ledger listing all unreconciled balances, overpayments, and duplicate payments.
- **FR-REP-006**: The system shall support exporting reports and grid datasets in standard formats: CSV, PDF, and JSON.

---

### 2.7 Rules Documentation & SOPs (`FR-DOC`)

- **FR-DOC-001**: The system shall maintain a centralized QA Rules Knowledge Base documenting every active, inactive, and deprecated validation rule.
- **FR-DOC-002**: The rule documentation shall include Rule ID, Title, DQ Dimension, Severity, Technical Description, SQL Logic / Definition, Business Impact Rationale, and Remediation SOP.
- **FR-DOC-003**: The system shall provide clickable deep-links from detected issues directly to the corresponding rule documentation page.
- **FR-DOC-004**: The system shall track version history and modification timestamps for all rule definitions.

---

### 2.8 User Management & Role-Based Access Control (`FR-USR`)

- **FR-USR-001**: The system shall support five predefined user roles: `Data Operations Analyst`, `QA Analyst`, `Operations Manager`, `System Administrator`, and `Read-Only / Reporting User`.
- **FR-USR-002**: The system shall restrict write, update, and resolve permissions according to the Role-Based Access Control (RBAC) matrix.
- **FR-USR-003**: The system shall prevent Read-Only users and Analysts from altering raw ingestion datasets or modifying system configuration parameters.
- **FR-USR-004**: The system shall enforce unique user credentials and secure session management.

---

### 2.9 AI-Assisted Operations & Root Cause Analysis (`FR-AI`)

- **FR-AI-001**: The system shall provide an AI-assisted issue explanation feature that generates human-readable root-cause summaries for verified SQL anomalies.
- **FR-AI-002**: The AI module shall receive bounded prompt contexts containing only verified rule metadata, failed query results, and affected synthetic claim attributes.
- **FR-AI-003**: The AI module shall output structured operational recommendations, including suspected root cause and suggested remediation steps.
- **FR-AI-004**: The system shall display explicit disclaimers indicating that AI explanations are advisory and that SQL QA rule outputs remain the authoritative source of truth.
- **FR-AI-005**: The system shall allow analysts to copy AI recommendations into the permanent investigation notes thread with a single click.

---

### 2.10 Auditability, Traceability & Logging (`FR-AUD`)

- **FR-AUD-001**: The system shall record an immutable, tamper-evident audit log entry for every state change, assignment, resolution, rule modification, and data batch execution.
- **FR-AUD-002**: Each audit log record shall capture `audit_id`, `timestamp`, `actor_user_id`, `action_type`, `entity_type`, `entity_id`, `previous_state`, `new_state`, and `client_ip`.
- **FR-AUD-003**: The system shall prevent all user roles (including System Administrators) from modifying, truncating, or deleting historical audit log entries.
- **FR-AUD-004**: The system shall provide an Audit Trail Explorer allowing filtered review of historical actions by entity, actor, date range, and action type.

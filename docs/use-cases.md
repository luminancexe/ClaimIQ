# ClaimIQ — Use Case Specifications

This document specifies the core operational use cases for the ClaimIQ platform (`UC-001` through `UC-016`). Each use case details the primary actor, preconditions, triggers, step-by-step main flow, alternate flows, failure scenarios, and postconditions.

---

## Use Case Index

| Use Case ID | Name | Primary Actor | Target Module |
| :--- | :--- | :--- | :--- |
| **UC-001** | View Overall Data-Quality Status | Data Ops Analyst / Manager | Dashboard & Overview |
| **UC-002** | Run QA Checks | QA Analyst / System Admin | QA Rule Engine |
| **UC-003** | Detect Duplicate Claims | System / QA Engine | QA Rule Engine |
| **UC-004** | Detect Missing Data | System / QA Engine | QA Rule Engine |
| **UC-005** | Detect Financial Discrepancies | System / QA Engine | Financial Reconciliation |
| **UC-006** | Detect Invalid Relationships | System / QA Engine | Referential Integrity |
| **UC-007** | Investigate an Issue | Data Ops Analyst | Investigation Workbench |
| **UC-008** | Assign an Issue | Data Ops Analyst / Manager | Issue Management |
| **UC-009** | Update Issue Status | Data Ops Analyst | Issue Lifecycle |
| **UC-010** | Document Investigation Findings | Data Ops Analyst | Investigation Workbench |
| **UC-011** | Review Audit History | Read-Only User / Auditor | Audit & Traceability |
| **UC-012** | Generate Operational Reports | Operations Manager / Analyst | Reporting Engine |
| **UC-013** | Filter Claims and Issues | Data Ops Analyst | Claims / Issue Explorer |
| **UC-014** | Search for a Specific Claim | Data Ops Analyst | Claims Search Engine |
| **UC-015** | Review QA Rule Documentation | QA Analyst / Analyst | Rules Knowledge Base |
| **UC-016** | Ask AI Assistant to Explain an Issue | Data Ops Analyst | AI Operations Assistant |

---

## Detailed Specifications

### UC-001: View Overall Data-Quality Status
- **Actor**: Data Operations Analyst, Operations Manager, QA Analyst
- **Preconditions**: User is authenticated and navigating to the ClaimIQ operational dashboard. Synthetic batch data has been processed.
- **Trigger**: User opens the ClaimIQ application or navigates to the Overview tab.
- **Main Flow**:
  1. System queries the latest data quality evaluation metrics.
  2. System displays the aggregate Data Quality (DQ) Score (0–100%).
  3. System displays key metrics: Total Processed Claims, Valid Claims Count, Detected Issues Count, Critical Issues Count, and Total Financial Discrepancy Amount ($).
  4. System renders visual charts: Issue Breakdown by Dimension (Completeness, Validity, Financial, Temporal, Referential), Severity Distribution (Critical, High, Medium, Low), and 30-Day Trend.
- **Expected Result**: User gains an immediate, comprehensive overview of system data health and urgent operational priorities.
- **Failure Scenarios**: No QA run data found $\rightarrow$ System displays prompt to execute initial QA batch check.

---

### UC-002: Run QA Checks
- **Actor**: QA Analyst, System Administrator, Data Operations Analyst
- **Preconditions**: Claims batch data is loaded in the database.
- **Trigger**: Actor clicks "Execute QA Batch" or an automated scheduler triggers batch execution.
- **Main Flow**:
  1. Actor selects target dataset/date range or chooses "Full Ingestion Run".
  2. Actor initiates execution.
  3. System executes active SQL QA validation rules sequentially/concurrently.
  4. System records rule execution timestamps, rows evaluated, and anomalies flagged.
  5. System persists new issue records in the issue tracking store.
  6. System updates overall Data Quality Index and summary metrics.
  7. System displays execution completion summary with runtime and detected count.
- **Expected Result**: All active QA rules run deterministically and populate the issue repository.
- **Failure Scenarios**: Database connection drops during execution $\rightarrow$ System rolls back batch transaction, logs error details, and alerts actor.

---

### UC-003: Detect Duplicate Claims
- **Actor**: System (Automated Rule Engine)
- **Preconditions**: Claims header and claim lines are populated in the database.
- **Trigger**: Execution of QA Rule `RULE-UNQ-001` during batch run.
- **Main Flow**:
  1. Rule executes SQL query grouping by `patient_id`, `provider_id`, `date_of_service`, `cpt_code`, and `billed_amount` where `count(*) > 1`.
  2. For each duplicate group identified, system records the duplicate claim IDs.
  3. System generates an issue with Category `Uniqueness`, Severity `High`, and associates the relevant claim records.
  4. Issue is placed into `Open` state in the issue queue.
- **Expected Result**: All identical claim submissions are accurately flagged without missing valid repeat encounters on different dates.
- **Failure Scenarios**: False positive on bilateral procedures performed on the same day $\rightarrow$ Rule checks procedure modifiers to ensure valid multi-unit billing is excluded.

---

### UC-004: Detect Missing Data
- **Actor**: System (Automated Rule Engine)
- **Preconditions**: Raw synthetic claims ingested.
- **Trigger**: Execution of Completeness QA rules (`RULE-CMP-xxx`).
- **Main Flow**:
  1. System scans mandatory fields across claim headers and lines (e.g., `patient_id`, `provider_npi`, `diagnosis_code`, `date_of_service`, `billed_amount`).
  2. System identifies records where mandatory fields are `NULL`, empty string, or whitespace.
  3. System generates issues categorizing missing fields by column and severity (e.g., missing NPI = `Critical`; missing secondary phone = `Low`).
  4. Issues are published to the triage queue with exact field-level pointers.
- **Expected Result**: 100% of incomplete records are flagged with exact missing field names.
- **Failure Scenarios**: Optional fields mistakenly flagged $\rightarrow$ Rule checks nullability constraints against schema dictionary.

---

### UC-005: Detect Financial Discrepancies
- **Actor**: System (Automated Rule Engine)
- **Preconditions**: Claims, payments, and adjustments tables are populated.
- **Trigger**: Execution of Financial Integrity QA rules (`RULE-FIN-xxx`).
- **Main Flow**:
  1. System checks for overpayments: `paid_amount > billed_amount`.
  2. System checks for negative values: `billed_amount < 0` or `paid_amount < 0`.
  3. System checks reconciliation equation: `ABS(billed_amount - (paid_amount + adjustment_amount + patient_responsibility)) > 0.01`.
  4. System flags discrepancy amounts, calculates dollar variance ($\Delta$), and logs `Critical` or `High` severity issues.
- **Expected Result**: All unbalanced financial entries and overpayments are isolated with variance amounts.
- **Failure Scenarios**: Rounding differences ($0.001) $\rightarrow$ Tolerance threshold of $\pm \$0.01$ applied to eliminate floating-point noise.

---

### UC-006: Detect Invalid Relationships
- **Actor**: System (Automated Rule Engine)
- **Preconditions**: Ingestion completed across entities.
- **Trigger**: Execution of Referential Integrity QA rules (`RULE-REF-xxx`).
- **Main Flow**:
  1. System executes left outer joins from claims to master patients, providers, and payers.
  2. System executes left outer joins from claim lines and payments to parent claims.
  3. Records with unmatched foreign keys are flagged as orphaned.
  4. System generates `Critical` referential integrity issues detailing the orphaned child record and the missing parent entity ID.
- **Expected Result**: All broken relationships and dangling records are captured before downstream reporting.
- **Failure Scenarios**: None; standard relational integrity check.

---

### UC-007: Investigate an Issue
- **Actor**: Data Operations Analyst
- **Preconditions**: Issue exists in the triage queue.
- **Trigger**: Analyst selects an issue from the queue.
- **Main Flow**:
  1. System loads the Issue Investigation Workbench for the selected issue ID.
  2. Workbench displays: Issue Metadata (Rule ID, Severity, Detected Timestamp, Status), Root-Cause Hypothesis, Affected Claim Header, Claim Lines, Patient/Provider references, and Payment history.
  3. System displays the exact SQL query and failed condition that triggered the issue.
  4. Analyst inspects associated records, compares values, and identifies the anomaly source.
- **Expected Result**: Analyst has complete context and historical records in a single interface to determine root cause.
- **Failure Scenarios**: Linked claim was deleted in synthetic refresh $\rightarrow$ System shows archived snapshot and warning notice.

---

### UC-008: Assign an Issue
- **Actor**: Data Operations Analyst, Operations Manager
- **Preconditions**: Issue exists with status `Open` or `Investigating`.
- **Trigger**: Actor clicks "Assign Issue" in the workbench or table view.
- **Main Flow**:
  1. Actor chooses an analyst from the user list or selects "Assign to Me".
  2. System updates the `assigned_to_user_id` on the issue.
  3. System logs an audit record: `Issue [ID] assigned to [User] by [Actor]`.
  4. Assigned user's active queue is updated.
- **Expected Result**: Ownership is clearly established, preventing duplicate analyst work.
- **Failure Scenarios**: Selected user is deactivated $\rightarrow$ System blocks assignment and displays validation error.

---

### UC-009: Update Issue Status
- **Actor**: Data Operations Analyst, Operations Manager
- **Preconditions**: Issue is assigned and currently open.
- **Trigger**: Analyst changes status dropdown in the workbench.
- **Main Flow**:
  1. Analyst selects new status: `Investigating`, `Resolved`, `False Positive`, `Escalated`, or `Ignored`.
  2. If status is `Resolved` or `False Positive`, system prompts for mandatory justification notes and root-cause category.
  3. Analyst enters required notes and confirms.
  4. System validates transition against Issue Lifecycle FSM.
  5. System persists updated status, resolution timestamp, and logs audit entry.
- **Expected Result**: Issue lifecycle advances in strict accordance with operational policy.
- **Failure Scenarios**: Analyst attempts to close issue without notes $\rightarrow$ System blocks transition and highlights mandatory fields.

---

### UC-010: Document Investigation Findings
- **Actor**: Data Operations Analyst
- **Preconditions**: Issue is open in Investigation Workbench.
- **Trigger**: Analyst enters text in the Investigation Notes section and clicks "Save Note".
- **Main Flow**:
  1. Analyst types markdown-formatted investigation notes (e.g., "Verified provider NPI mismatch against master registry; billing taxonomy 207Q00000X was submitted instead of 208D00000X").
  2. Analyst selects Root-Cause Category (e.g., `Configuration Error`, `Vendor Mapping Bug`, `Payer Adjudication Flaw`, `Data Entry Typo`).
  3. System saves note with immutable timestamp and analyst ID.
  4. System appends note to chronological discussion thread.
- **Expected Result**: Findings are permanently recorded and available for future audits or team reference.
- **Failure Scenarios**: Empty submission $\rightarrow$ System prompts for text.

---

### UC-011: Review Audit History
- **Actor**: Read-Only User, Auditor, Operations Manager
- **Preconditions**: Historical events have occurred.
- **Trigger**: User navigates to "Audit Trail" tab or views issue change history.
- **Main Flow**:
  1. User specifies filter criteria: Entity Type (`Claim`, `Issue`, `Rule`, `User`), Date Range, Actor ID, or Action Type.
  2. System queries the immutable `audit_log` repository.
  3. System displays chronological audit table showing: Timestamp, Actor, Action, Entity ID, Previous State, New State, and IP/Session reference.
  4. User can inspect JSON diff of altered fields.
- **Expected Result**: Complete, tamper-evident visibility into every operational action and data alteration.
- **Failure Scenarios**: None; audit log is read-only.

---

### UC-012: Generate Operational Reports
- **Actor**: Operations Manager, Data Operations Analyst
- **Preconditions**: Issues and QA batches have been recorded.
- **Trigger**: User navigates to Reports section and selects report template.
- **Main Flow**:
  1. User chooses report type: `Daily Data Quality Summary`, `Weekly Operations Report`, `Provider Quality Scorecard`, `Payer Adjudication Report`, or `Financial Discrepancy Ledger`.
  2. User selects reporting window (e.g., "Last 7 Days", "Month to Date", Custom Range).
  3. System aggregates metrics, compiles tables, and generates chart visualizations.
  4. User reviews report on-screen and clicks "Export (PDF / CSV / XLSX)".
  5. System streams downloadable report package.
- **Expected Result**: High-quality, presentation-ready operational reports generated on demand.
- **Failure Scenarios**: Large date range causing timeout $\rightarrow$ System uses pre-aggregated summary tables for rapid rendering.

---

### UC-013: Filter Claims and Issues
- **Actor**: Data Operations Analyst, QA Analyst
- **Preconditions**: User is in Claims Explorer or Issue Queue.
- **Trigger**: User adjusts search filters in the UI.
- **Main Flow**:
  1. User applies combination of filters: Severity (`Critical`, `High`), Status (`Open`, `Investigating`), Category (`Financial`, `Referential`), Date Range, Payer ID, or Provider ID.
  2. System updates URL query parameters and executes dynamic parameterized SQL query.
  3. Table updates in real-time with filtered records, displaying pagination and total match count.
- **Expected Result**: Analyst rapidly narrows down high-priority subsets of claims or issues.
- **Failure Scenarios**: Filter yields zero results $\rightarrow$ System displays helpful empty state with "Reset Filters" action.

---

### UC-014: Search for a Specific Claim
- **Actor**: Data Operations Analyst
- **Preconditions**: User has a Claim ID, Patient ID, Provider NPI, or Check/Trace Number.
- **Trigger**: User types query into global search bar and presses Enter.
- **Main Flow**:
  1. System executes targeted lookup across indexed fields (`claim_id`, `patient_id`, `provider_npi`, `check_number`).
  2. System displays search results grouped by entity.
  3. User clicks matching claim.
  4. System opens Claim Detail view displaying full header, claim lines, linked payments, associated QA issues, and audit history.
- **Expected Result**: Instant retrieval of exact claim record with all associated contextual data.
- **Failure Scenarios**: Record not found $\rightarrow$ System suggests verifying identifier format or checking archived batches.

---

### UC-015: Review QA Rule Documentation
- **Actor**: QA Analyst, Data Operations Analyst
- **Preconditions**: User is researching a specific rule failure.
- **Trigger**: User clicks "Rule Docs" or clicks the rule code link from an issue card.
- **Main Flow**:
  1. System opens the Rules Knowledge Base for the specified rule ID (e.g., `RULE-FIN-001`).
  2. System displays: Rule Name, Description, DQ Dimension, Default Severity, Rationale / Operational Impact, SQL Definition / Logic, Remediation Steps, and Version History.
  3. Analyst reviews standard operating procedures (SOP) for resolving this rule type.
- **Expected Result**: Standardized documentation ensures consistent investigation and remediation across the team.
- **Failure Scenarios**: Rule is deprecated $\rightarrow$ System displays deprecation banner and links to successor rule.

---

### UC-016: Ask AI Assistant to Explain an Issue
- **Actor**: Data Operations Analyst
- **Preconditions**: Issue has been detected and verified by the SQL QA engine.
- **Trigger**: Analyst clicks "Explain with ClaimIQ AI" on an issue detail card.
- **Main Flow**:
  1. System packages the verified issue context: Rule definition, failed SQL criteria, affected claim header, line items, and financial values.
  2. System sends prompt to the local AI assistant module (strictly bounded to the verified issue data).
  3. AI Assistant analyzes the discrepancy and generates a structured explanation:
     - Plain-language explanation of the discrepancy.
     - Probable root cause (e.g., missing modifier, calculation mismatch, timing race condition).
     - Recommended operational next steps for the analyst.
  4. Analyst reviews AI explanation and can copy insights directly into Investigation Notes.
- **Expected Result**: Faster root-cause identification and accelerated onboarding for junior analysts.
- **Failure Scenarios**: AI explanation hallucinates or contradicts SQL evidence $\rightarrow$ System displays disclaimer that SQL rule output is the authoritative source of truth, and analyst must verify findings before resolving.

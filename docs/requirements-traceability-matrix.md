# ClaimIQ — Requirements Traceability Matrix (RTM)

## 1. Priority Model & Governance

ClaimIQ uses a four-level priority classification to govern implementation phases:

- **P0 (Essential / MVP Core)**: Non-negotiable foundational requirements necessary for core data operations, SQL QA validation, and data integrity.
- **P1 (Important / Core Operations)**: High-priority capabilities required for complete analyst workflow, issue lifecycle management, and standard reporting.
- **P2 (Enhancement / Advanced Operations)**: Advanced features that improve operational efficiency, provider/payer scorecards, and batch management.
- **P3 (Optional / Future Innovation)**: Advanced integrations such as AI-assisted root-cause explanations and extended file export options.

---

## 2. Comprehensive Traceability Matrix

| Requirement ID | Requirement Summary | Category | Priority | Target Phase | Validation Method | Current Status |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| **FR-DM-001** | Store synthetic patient master records | Data Mgmt | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-DM-002** | Store synthetic provider records with NPI | Data Mgmt | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-DM-003** | Store synthetic healthcare facility records | Data Mgmt | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-DM-004** | Store synthetic payer records with filing limits | Data Mgmt | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-DM-005** | Store synthetic clinical encounter records | Data Mgmt | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-DM-006** | Support batch ingestion of synthetic datasets | Data Mgmt | **P0** | Phase 3 | Ingestion Pipeline Test | Specified |
| **FR-DM-007** | Strict synthetic data isolation (Zero PHI) | Data Mgmt | **P0** | Phase 3 | Security Audit & Code Scan | Specified |
| **FR-QA-001** | Execute automated SQL data quality rules | QA Engine | **P0** | Phase 5 | Automated SQL QA Suite | Specified |
| **FR-QA-002** | Categorize rules across 7 DQ dimensions | QA Engine | **P0** | Phase 5 | Rule Metadata Verification | Specified |
| **FR-QA-003** | Assign default severity levels (Critical–Low) | QA Engine | **P0** | Phase 5 | Rule Schema Test | Specified |
| **FR-QA-004** | Detect duplicate claims on identical DOS/CPT | QA Engine | **P0** | Phase 5 | Injected Duplicate Test | Specified |
| **FR-QA-005** | Detect missing mandatory fields | QA Engine | **P0** | Phase 5 | Null Field Injection Test | Specified |
| **FR-QA-006** | Verify format validity (NPI Luhn, CPT, ICD-10) | QA Engine | **P0** | Phase 5 | Invalid Format Test | Specified |
| **FR-QA-007** | Flag temporal sequence violations | QA Engine | **P0** | Phase 5 | Chronological Anomaly Test | Specified |
| **FR-QA-008** | Detect orphaned records and referential breaks | QA Engine | **P0** | Phase 5 | Orphan Foreign Key Test | Specified |
| **FR-QA-009** | Compute aggregate Data Quality (DQ) Score | QA Engine | **P0** | Phase 6 | Formula Unit Test | Specified |
| **FR-QA-010** | Support manual and scheduled batch execution | QA Engine | **P1** | Phase 5 | API Runner Test | Specified |
| **FR-QA-011** | Log rule execution telemetry and latency | QA Engine | **P1** | Phase 5 | Execution Telemetry Test | Specified |
| **FR-CLM-001** | Store claim header records with status | Claims | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-CLM-002** | Store itemized claim line records | Claims | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-CLM-003** | Multi-attribute claims search and filtering | Claims | **P1** | Phase 7/8 | API & UI Integration Test | Specified |
| **FR-CLM-004** | Comprehensive claim detail view | Claims | **P1** | Phase 8 | UI Component Test | Specified |
| **FR-CLM-005** | Validate header billed sum equals line sums | Claims | **P0** | Phase 5 | SQL Validation Rule | Specified |
| **FR-ANL-001** | Store payment transaction records | Analytics | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-ANL-002** | Store adjustment and denial records | Analytics | **P0** | Phase 2 | Schema DDL & Seed Test | Specified |
| **FR-ANL-003** | Detect overpayments (Paid $>$ Billed) | Analytics | **P0** | Phase 5 | Injected Overpayment Test | Specified |
| **FR-ANL-004** | Detect negative monetary values | Analytics | **P0** | Phase 5 | Negative Value Injection | Specified |
| **FR-ANL-005** | Detect reconciliation equation discrepancies | Analytics | **P0** | Phase 5 | Financial Balancing Test | Specified |
| **FR-ANL-006** | Detect duplicate payment transactions | Analytics | **P0** | Phase 5 | Duplicate Payment Test | Specified |
| **FR-ANL-007** | Aggregate total financial variance at risk | Analytics | **P1** | Phase 6 | Financial Rollup Test | Specified |
| **FR-ISS-001** | Automatically generate unique issue records | Issues | **P0** | Phase 5 | Engine Generation Test | Specified |
| **FR-ISS-002** | Enforce issue lifecycle state machine | Issues | **P0** | Phase 7/9 | FSM State Transition Test | Specified |
| **FR-ISS-003** | Enforce user assignment before investigation | Issues | **P1** | Phase 7/9 | Validation Rule & API Test | Specified |
| **FR-ISS-004** | Provide Issue Investigation Workbench UI | Issues | **P0** | Phase 9 | UI E2E Test | Specified |
| **FR-ISS-005** | Require root-cause category upon resolution | Issues | **P0** | Phase 7/9 | Mandatory Field Test | Specified |
| **FR-ISS-006** | Require justification notes for resolutions | Issues | **P0** | Phase 7/9 | Mandatory Field Test | Specified |
| **FR-ISS-007** | Support user and team assignment | Issues | **P1** | Phase 7/9 | Assignment API Test | Specified |
| **FR-ISS-008** | Support bulk triage and status updates | Issues | **P2** | Phase 9 | Bulk Action Test | Specified |
| **FR-REP-001** | Generate Daily Data Quality Report | Reporting | **P0** | Phase 6/8 | Report Output Test | Specified |
| **FR-REP-002** | Generate Weekly Operations & SLA Report | Reporting | **P1** | Phase 6/8 | Metrics Rollup Test | Specified |
| **FR-REP-003** | Generate Provider Quality Scorecard | Reporting | **P1** | Phase 6/8 | Provider Aggregation Test | Specified |
| **FR-REP-004** | Generate Payer Adjudication Report | Reporting | **P1** | Phase 6/8 | Payer Aggregation Test | Specified |
| **FR-REP-005** | Generate Financial Discrepancy Ledger | Reporting | **P0** | Phase 6/8 | Ledger Export Test | Specified |
| **FR-REP-006** | Support export to CSV, PDF, and JSON | Reporting | **P1** | Phase 9 | File Stream Test | Specified |
| **FR-DOC-001** | Maintain centralized QA Rules Knowledge Base | Documentation| **P1** | Phase 10 | Content & UI Test | Specified |
| **FR-DOC-002** | Document rule SQL logic and remediation SOPs | Documentation| **P1** | Phase 10 | Knowledge Base Audit | Specified |
| **FR-DOC-003** | Deep-link issues directly to rule documentation | Documentation| **P1** | Phase 9/10 | Deep-Link Navigation Test | Specified |
| **FR-DOC-004** | Version control for rule definitions | Documentation| **P2** | Phase 10 | History Tracking Test | Specified |
| **FR-USR-001** | Support 5 predefined user roles | Users/RBAC | **P0** | Phase 7 | RBAC Authorization Test | Specified |
| **FR-USR-002** | Enforce RBAC permission matrix | Users/RBAC | **P0** | Phase 7 | Security Permission Test | Specified |
| **FR-USR-003** | Restrict raw data mutations for non-admins | Users/RBAC | **P0** | Phase 7 | Security Boundary Test | Specified |
| **FR-USR-004** | Enforce secure credentials and sessions | Users/RBAC | **P1** | Phase 7/11 | Auth Security Test | Specified |
| **FR-AI-001** | Generate AI-assisted issue explanations | AI Operations | **P3** | Phase 12 | LLM Prompt & Output Test | Specified |
| **FR-AI-002** | Restrict AI prompts to verified SQL context | AI Operations | **P3** | Phase 12 | Context Isolation Test | Specified |
| **FR-AI-003** | Output structured root-cause recommendations | AI Operations | **P3** | Phase 12 | Schema Validation Test | Specified |
| **FR-AI-004** | Display advisory disclaimers on AI output | AI Operations | **P3** | Phase 12 | UI Verification | Specified |
| **FR-AI-005** | One-click copy AI findings into notes thread | AI Operations | **P3** | Phase 12 | UI Interaction Test | Specified |
| **FR-AUD-001** | Append-only immutable audit logging | Auditability | **P0** | Phase 2/7 | Audit Immutability Test | Specified |
| **FR-AUD-002** | Capture full state before and after change | Auditability | **P0** | Phase 2/7 | JSON Diff Verification | Specified |
| **FR-AUD-003** | Prevent deletion or truncation of audit logs | Auditability | **P0** | Phase 2/11 | DB Permission & Trigger | Specified |
| **FR-AUD-004** | Audit Trail Explorer with search and filter | Auditability | **P1** | Phase 8/9 | Audit UI Explorer Test | Specified |

---

## 3. Non-Functional Requirements Traceability

| Requirement ID | Summary | Category | Priority | Target Phase | Validation Method | Status |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| **NFR-DI-001** | Deterministic QA execution ($100\%$) | Data Integrity | **P0** | Phase 5 | Repeated Run Hash Test | Specified |
| **NFR-DI-002** | ACID transaction compliance | Data Integrity | **P0** | Phase 2/7 | Rollback & Commit Test | Specified |
| **NFR-DI-003** | Fixed-point financial precision | Data Integrity | **P0** | Phase 2 | Precision Boundary Test | Specified |
| **NFR-PRF-001** | 100k claims QA execution $<30$s | Performance | **P0** | Phase 5 | Benchmark Load Test | Specified |
| **NFR-PRF-002** | Dashboard $p95$ latency $<200$ms | Performance | **P1** | Phase 7/8 | Load & Latency Test | Specified |
| **NFR-PRF-003** | Search/filter latency $<300$ms | Performance | **P1** | Phase 7/8 | Filter Query Benchmark | Specified |
| **NFR-PRF-004** | Relational scale up to 1M claims | Scalability | **P1** | Phase 2/5 | 1M Record Stress Test | Specified |
| **NFR-SEC-001** | Zero PHI containment enforcement | Security | **P0** | Phase 3/11 | Automated Code/Data Scan | Specified |
| **NFR-SEC-002** | RBAC token authorization | Security | **P0** | Phase 7 | Security Pen Test | Specified |
| **NFR-SEC-003** | SQL injection prevention | Security | **P0** | Phase 7 | Static Analysis & DAST | Specified |
| **NFR-REL-001** | Single-rule error fault isolation | Reliability | **P0** | Phase 5 | Injected Rule Syntax Error | Specified |
| **NFR-REL-002** | Reproducible schema & seed generation | Reliability | **P0** | Phase 3/11 | Clean Environment Rebuild | Specified |

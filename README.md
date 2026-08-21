# ClaimIQ

### Healthcare Claims Data Quality & Operations Platform

ClaimIQ is a synthetic-data healthcare Revenue Cycle Management (RCM) data quality and operations platform designed to identify claims-data discrepancies, validate operational workflows, support issue investigation, and provide actionable analytics and reporting.

The project is developed as a rigorous, phased software engineering portfolio project demonstrating core competencies in **SQL, MySQL 8.x, relational data modeling, data quality assurance, data integrity, operational analytics, root-cause investigation, documentation, and AI-assisted analysis**.

> **Important:** ClaimIQ operates exclusively on synthetic healthcare data. It does not process real patient information, Protected Health Information (PHI), real insurance records, real claims, or live healthcare billing systems.

---

## 📊 Current Project Status

```text
Phase 1: Domain Research, Scope & Requirements   ████████████████████  COMPLETE
Phase 2: Database Architecture & Data Modeling    ████████████████████  COMPLETE
Phase 3: Synthetic Data Generation Engine         ░░░░░░░░░░░░░░░░░░░░  NEXT
Phase 4: Controlled Error Injection Engine        ░░░░░░░░░░░░░░░░░░░░  PLANNED
Phase 5: SQL Data Quality Engine                  ░░░░░░░░░░░░░░░░░░░░  PLANNED
Phase 6: Python Analytics & Metrics Engine        ░░░░░░░░░░░░░░░░░░░░  PLANNED
Phase 7: Backend & API Development                ░░░░░░░░░░░░░░░░░░░░  PLANNED
Phase 8: Operations Dashboard & UI                ░░░░░░░░░░░░░░░░░░░░  PLANNED
Phase 9: Investigation Workbench & Reporting      ░░░░░░░░░░░░░░░░░░░░  PLANNED
Phase 10: SOP & Documentation Knowledge Base      ░░░░░░░░░░░░░░░░░░░░  PLANNED
Phase 11: Testing, Security & Performance         ░░░░░░░░░░░░░░░░░░░░  PLANNED
Phase 12: AI Intelligence & Final Release         ░░░░░░░░░░░░░░░░░░░░  PLANNED
```

---

## 🎯 Project Mission

Healthcare Revenue Cycle Management depends on large volumes of interconnected operational and financial data. Even minor data inconsistencies can result in clearinghouse rejections, delayed reimbursements, unverified write-offs, compliance vulnerabilities, and downstream financial leakages.

ClaimIQ simulates an enterprise data operations platform where analysts can:

- Validate healthcare claims data across 7 core quality dimensions
- Detect data-quality anomalies, formatting defects, and missing attributes
- Identify financial discrepancies, overpayments, and reconciliation variances
- Detect broken referential relationships and invalid business-state transitions
- Investigate operational issues within a dedicated investigation workbench
- Track issue resolution through an auditable lifecycle state machine
- Monitor data-quality trends, clean claim pass rates, and SLA compliance
- Generate operational reports, provider scorecards, and payer denial analyses
- Maintain standardized QA rules and standard operating procedures (SOPs)
- Utilize AI to assist with the explanation and root-cause analysis of verified issues

The goal is not to recreate a production healthcare billing gateway, but to demonstrate how a modern data operations platform maintains **accuracy, consistency, traceability, and operational quality** across complex claims pipelines.

---

## 🏥 RCM Domain Overview

ClaimIQ models a simplified 9-stage healthcare Revenue Cycle Management lifecycle:

```text
Patient Registration
        ↓
Clinical Encounter
        ↓
Charge Capture & Claim Creation (Synthetic 837)
        ↓
Electronic Claim Submission
        ↓
Payer Pre-Adjudication Edits
        ↓
Payer Adjudication (Accepted / Rejected / Denied)
        ↓
Payment Disbursement & Remittance (Synthetic 835 ERA)
        ↓
Financial Reconciliation (Billed = Paid + Adj + PatResp)
        ↓
Account Resolution & Closure
```

The platform uses synthetic representations of 15 standard RCM entities:

- **Patients**: Demographics and policy memberships
- **Providers**: Clinicians with 10-digit NPIs and taxonomy codes
- **Facilities**: Clinics, hospitals, and billing Tax IDs (TIN)
- **Payers & Plans**: Commercial, Medicare, and Medicaid insurers
- **Encounters**: Clinical episodes linking patients, providers, and dates of service (DOS)
- **Procedures & Diagnoses**: Synthetic CPT/HCPCS and ICD-10-CM code sets
- **Claims & Claim Lines**: Header and itemized service line charges
- **Payments & Adjustments**: Cash disbursements and CARC/RARC contractual write-offs
- **Denials & Remittances**: Electronic remittance batches and refusal reason codes
- **Reconciliations**: Mathematical account balancing and variance detection

---

## 🔎 Problems ClaimIQ Addresses

ClaimIQ detects and triages five major categories of operational claims anomalies:

### 1. Data Quality & Formatting Defects
- Missing mandatory fields (NPI, primary diagnosis, date of service)
- Duplicate claims sharing identical patient, provider, DOS, and CPT codes
- Malformed identifiers (invalid 10-digit NPI Luhn checksums)
- Inconsistent coding syntax and unstandardized abbreviations

### 2. Financial Discrepancies
- Overpayments where disbursed payment exceeds total billed charge ($\text{Paid} > \text{Billed}$)
- Negative monetary values in charges or disbursements without reversal flags
- Duplicate payment postings sharing identical remittance trace numbers
- Reconciliation mismatches where $\text{Billed} \neq \text{Paid} + \text{Adjustment} + \text{PatientResp}$
- Itemization discrepancies where header billed amount does not equal the sum of claim lines

### 3. Temporal Anomalies
- Electronic submission date recorded prior to date of service ($\text{Submission} < \text{DOS}$)
- Payment or remittance date preceding claim submission date
- Payer denial determination recorded before submission
- Future-dated clinical or billing events

### 4. Referential Integrity Failures
- Orphaned claims referencing non-existent patients, providers, or payers
- Payments or claim lines referencing non-existent parent claim records
- Unmapped facility or plan foreign keys

### 5. Business Logic & State Violations
- Claims marked `Paid` with $\$0.00$ payment and zero contractual adjustments
- Claims marked `Denied` containing positive disbursed cash payments
- Claims marked `Pending` with active check/trace numbers
- Claim headers existing without itemized service lines

---

## 🛠️ Official Technology Standards

| Domain / Area | Technology / Standard | Implementation Role |
| :--- | :--- | :--- |
| **Database Engine** | **MySQL 8.x** | Official relational database management system |
| **Storage Engine** | **InnoDB** | Enforces row-level locking, ACID transactions, and foreign key integrity |
| **Character Set & Collation**| **`utf8mb4` / `utf8mb4_0900_ai_ci`** | Complete 4-byte Unicode encoding |
| **Query Language** | **SQL** | Relational DDL, queries, and QA validation rules |
| **Financial Precision** | **`DECIMAL(12, 2)`** | Exact fixed-point arithmetic for all monetary values |
| **Temporal Standard** | **`DATETIME(6)` (UTC)** | Microsecond timestamp precision with canonical UTC timezone |
| **Identifier Strategy** | **`BIGINT UNSIGNED` + `VARCHAR(64)`** | Internal surrogate PKs + unique external business reference keys |
| **Data Generation** | **Python** | Deterministic synthetic claims generator *(Phase 3)* |
| **Analytics Engine** | **Python / Pandas** | Data quality index and SLA metrics *(Phase 6)* |
| **Backend API** | **FastAPI (Python)** | RESTful API service layer *(Phase 7)* |
| **Frontend UI** | **React / Vite** | Web-based operational dashboard & workbench *(Phase 8)* |
| **AI Layer** | **LLM Integration** | Verified issue explanation & root-cause assistance *(Phase 12)* |

---

## 🏛️ Database Architecture

ClaimIQ's relational schema is partitioned into nine cohesive operational domains across 22 normalized tables:

```text
ClaimIQ Database (MySQL 8.x / InnoDB / utf8mb4)
│
├── Reference Domain
│   ├── Claim Statuses (ref_claim_statuses)
│   ├── Issue Statuses (ref_issue_statuses)
│   ├── Severities (ref_severities)
│   ├── Data Quality Dimensions (ref_dq_dimensions)
│   ├── Root Causes (ref_root_causes)
│   └── Adjustment Group Codes (ref_adjustment_group_codes)
│
├── Patient & Provider Domain
│   ├── Patients (patients)
│   ├── Facilities (facilities)
│   ├── Providers (providers)
│   ├── Payers (payers)
│   ├── Insurance Plans (insurance_plans)
│   └── Patient Coverage (patient_coverage)
│
├── Clinical & Encounter Domain
│   ├── Encounters (encounters)
│   └── Encounter Diagnoses (encounter_diagnoses)
│
├── Claims Domain
│   ├── Claims Header (claims)
│   ├── Itemized Claim Lines (claim_lines)
│   └── Claim Status History (claim_status_history)
│
├── Financial & Reconciliation Domain
│   ├── Remittances (remittances)
│   ├── Payments (payments)
│   ├── Adjustments (adjustments)
│   ├── Denials (denials)
│   └── Reconciliations (reconciliations)
│
├── Operations & QA Domain
│   ├── QA Rule Categories (qa_rule_categories)
│   ├── QA Rules (qa_rules)
│   ├── QA Execution Runs (qa_execution_runs)
│   ├── QA Results (qa_results)
│   ├── Issues (issues)
│   ├── Issue History (issue_history)
│   └── Issue Notes (issue_notes)
│
└── Audit Domain
    └── Audit Events (audit_events)
```

---

## 📚 Completed Phases & Deliverables

### Phase 1 — Domain Research, Scope & Requirements Definition
- **16 Formal Use Cases** ([`docs/use-cases.md`](docs/use-cases.md)): `UC-001` through `UC-016` specifying actors, triggers, main flows, and failure modes.
- **60+ Functional Requirements** ([`docs/functional-requirements.md`](docs/functional-requirements.md)): Numbered requirements across 10 functional domains.
- **Quantitative Non-Functional Requirements** ([`docs/non-functional-requirements.md`](docs/non-functional-requirements.md)): Benchmarks for performance ($<30$s for 100k claims), scalability (1M records), auditability, and data determinism.
- **7-Dimension Healthcare Data Quality Framework** ([`docs/data-quality-framework.md`](docs/data-quality-framework.md)): Formulas for weighted composite Data Quality Scores.
- **4-Tier Severity & SLA Model** ([`docs/severity-model.md`](docs/severity-model.md)): Critical, High, Medium, and Low triage timelines and escalation pathways.
- **State Machine Specifications**: Claim Lifecycle FSM ([`docs/claim-lifecycle.md`](docs/claim-lifecycle.md)) and Issue Lifecycle FSM ([`docs/issue-lifecycle.md`](docs/issue-lifecycle.md)).
- **Standard Operating Procedures** ([`docs/operational-workflow.md`](docs/operational-workflow.md)): 10-step daily operational lifecycle and hourly triage cadence.
- **Operational Reporting Specifications** ([`docs/reporting-requirements.md`](docs/reporting-requirements.md)): Detailed requirements for 8 core operations reports.
- **Requirements Traceability Matrix** ([`docs/requirements-traceability-matrix.md`](docs/requirements-traceability-matrix.md)): Complete P0–P3 priority mapping.
- **Phase 1 Completion Report** ([`PHASE_1_COMPLETION_REPORT.md`](PHASE_1_COMPLETION_REPORT.md)): Formal verification sign-off.

### Phase 2 — Database Architecture & Data Modeling
- **Official MySQL 8.x Architecture** ([`docs/database-architecture.md`](docs/database-architecture.md)): Complete relational design using InnoDB, utf8mb4, and canonical UTC datetime.
- **Entity-Relationship Diagram** ([`docs/entity-relationship-diagram.md`](docs/entity-relationship-diagram.md)): System-wide and domain-specific Mermaid ERDs covering all 22 tables.
- **Comprehensive Data Dictionary** ([`docs/data-dictionary.md`](docs/data-dictionary.md)): Detailed documentation for 22 tables and 124 columns with MySQL 8.x types, keys, constraints, and allowed values.
- **Normalization Strategy (3NF)** ([`docs/normalization-strategy.md`](docs/normalization-strategy.md)): Functional dependency maps, anomaly prevention, and justified summary snapshot structures.
- **Index Strategy** ([`docs/index-strategy.md`](docs/index-strategy.md)): Matrix of clustered primary keys, secondary foreign key indexes, and composite queue triage indexes.
- **Database Conventions** ([`docs/database-conventions.md`](docs/database-conventions.md)): Strict naming conventions (`pk_`, `fk_`, `uq_`, `idx_`, `chk_`) and dual identifier architecture.
- **Claim & Financial Reconciliation Model** ([`docs/claim-data-model.md`](docs/claim-data-model.md)): Itemization invariants, state tracking, and variance balancing.
- **Modular DDL & Migration Scripts** ([`database/schema/`](database/schema/)): 9 clean SQL schema files and consolidated idempotent migration [`database/migrations/001_initial_schema.sql`](database/migrations/001_initial_schema.sql).
- **Schema Validation Test Runner** ([`database/validate_schema.py`](database/validate_schema.py)): Python test harness validating table creation, reference seeds, valid insert pipelines, and constraint rejection on MySQL 8.x.
- **Schema Validation Report** ([`docs/phase-2-schema-validation.md`](docs/phase-2-schema-validation.md)): Test execution results and verification matrix.
- **Phase 2 Completion Report** ([`PHASE_2_COMPLETION_REPORT.md`](PHASE_2_COMPLETION_REPORT.md)): Verification sign-off for Phase 2.

---

## 📂 Repository Structure

```text
ClaimIQ/
│
├── docs/                                    # Comprehensive Project Documentation
│   ├── project-overview.md                  # Project identity, problem statement & non-goals
│   ├── rcm-domain-overview.md               # Healthcare RCM lifecycle & core entity glossary
│   ├── problem-definition.md                # 5 anomaly categories & operational impact
│   ├── users-and-roles.md                   # 5 user personas & Role-Based Access Control matrix
│   ├── use-cases.md                         # Use cases UC-001 through UC-016
│   ├── functional-requirements.md           # 60+ functional requirements across 10 domains
│   ├── non-functional-requirements.md       # Performance, scalability, security & auditability
│   ├── data-quality-framework.md            # 7 DQ dimensions & composite DQ score formula
│   ├── severity-model.md                    # 4-tier severity triage & SLA resolution targets
│   ├── claim-lifecycle.md                   # Claim FSM & state transition anomaly matrix
│   ├── issue-lifecycle.md                   # Issue FSM & root-cause categorization taxonomy
│   ├── operational-workflow.md              # 10-step daily operational lifecycle & analyst SOP
│   ├── reporting-requirements.md            # Specifications for 8 operational reports
│   ├── success-metrics.md                   # System technical metrics vs. Business RCM KPIs
│   ├── project-scope.md                     # In-scope/out-of-scope & 12-phase dependency roadmap
│   ├── requirements-traceability-matrix.md  # Full RTM linking requirements to MySQL 8.x schema
│   │
│   ├── database-architecture.md             # MySQL 8.x technology decision & layer design
│   ├── entity-relationship-diagram.md       # High-level & domain-specific Mermaid ER diagrams
│   ├── data-dictionary.md                   # Complete 22-table data dictionary
│   ├── normalization-strategy.md            # 3NF normalization analysis & functional dependencies
│   ├── index-strategy.md                    # B-Tree index matrix & query performance rationales
│   ├── database-conventions.md              # Naming standards & dual identifier architecture
│   ├── claim-data-model.md                  # Claim header-to-line invariants & reconciliation
│   └── phase-2-schema-validation.md         # MySQL 8.x schema validation test specifications
│
├── database/                                # MySQL 8.x Database Schema & Migrations
│   ├── schema/
│   │   ├── 01_reference_tables.sql          # Lookup tables (statuses, severities, DQ dimensions)
│   │   ├── 02_patient_provider_tables.sql   # Patients, facilities, providers, payers, plans
│   │   ├── 03_clinical_encounter_tables.sql # Encounters & diagnoses
│   │   ├── 04_claims_tables.sql             # Claims, claim lines & claim status history
│   │   ├── 05_financial_tables.sql          # Remittances, payments, adjustments, reconciliations
│   │   ├── 06_operations_qa_tables.sql      # QA rules, execution runs, results, issues, notes
│   │   ├── 07_audit_tables.sql              # Immutable audit events log table
│   │   ├── 08_indexes.sql                   # Foreign key, search & composite secondary indexes
│   │   └── 09_seed_reference_data.sql       # Static seed data for reference tables
│   │
│   ├── migrations/
│   │   └── 001_initial_schema.sql           # Consolidated reproducible MySQL 8.x migration
│   │
│   └── validate_schema.py                   # Python MySQL 8.x schema validation test suite
│
├── PHASE_1_COMPLETION_REPORT.md             # Formal sign-off for Phase 1
├── PHASE_2_COMPLETION_REPORT.md             # Formal sign-off for Phase 2
└── README.md                                # Root Project Documentation & Architecture
```

---

## 📋 Complete 12-Phase Project Roadmap

| Phase # | Phase Title | Core Objectives | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Domain Research, Scope & Requirements** | Formal use cases, FRs, NFRs, DQ framework, FSMs, RTM | ✅ **Complete** |
| **Phase 2** | **Database Architecture & Data Modeling** | MySQL 8.x relational schema, 22 tables, ERDs, DDL, migrations, validation | ✅ **Complete** |
| **Phase 3** | **Synthetic Data Generation Engine** | Deterministic Python generator producing clean, referentially valid datasets | 🔜 **Next** |
| **Phase 4** | **Controlled Error Injection Engine** | Systematic injector introducing targeted anomalies at configurable rates | ⏳ Planned |
| **Phase 5** | **SQL Data Quality Engine** | Modular SQL validation queries auditing 7 DQ dimensions and generating issues | ⏳ Planned |
| **Phase 6** | **Python Analytics Engine** | Metrics computation, composite DQ scores, MTTR, and financial rollups | ⏳ Planned |
| **Phase 7** | **Backend API & Service Layer** | RESTful FastAPI backend implementing claims, issues, rules, and audit APIs | ⏳ Planned |
| **Phase 8** | **Operations Dashboard & UI** | React/Vite web application with executive KPI cards and claims explorer | ⏳ Planned |
| **Phase 9** | **Investigation Workbench & Reporting** | Issue detail inspection UI, markdown investigation notes, PDF/CSV report exports | ⏳ Planned |
| **Phase 10** | **SOP & Documentation Knowledge Base** | In-app rule documentation viewer and operational runbooks | ⏳ Planned |
| **Phase 11** | **Testing, Security & Performance** | Automated regression suites, RBAC authorization enforcement, Docker containerization | ⏳ Planned |
| **Phase 12** | **AI Intelligence & Final Release** | Local LLM integration for verified issue explanation and portfolio packaging | ⏳ Planned |

---

## 🔜 Next — Phase 3: Synthetic Data Generation

Phase 3 will design and implement a **deterministic, configurable synthetic healthcare claims data generator** in Python to populate the Phase 2 MySQL 8.x schema with clean baseline data.

### Planned Phase 3 Capabilities
- **Deterministic Reproducibility**: Seeded random generation ensuring identical dataset reproduction across test runs.
- **Full Relational Integrity**: 100% valid foreign key relationships across patients, facilities, providers, payers, plans, encounters, claims, claim lines, payments, and remittances.
- **Configurable Scale**: Ability to generate small development batches (1,000 claims) or large stress-testing datasets (100,000+ claims).
- **Realistic Healthcare Distributions**: Realistic procedural coding sets (CPT), diagnostic codes (ICD-10), Luhn-valid 10-digit NPIs, and realistic financial fee schedule curves.

*(Note: Controlled data corruption and defect injection are strictly decoupled and belong to Phase 4).*

---

## 🔐 Data Governance & Privacy Mandate

ClaimIQ is architected around strict synthetic data isolation:
- **Zero Real PHI**: No real patient records, Social Security Numbers, or actual Medical Record Numbers (MRNs) are ever ingested or processed.
- **Zero Production Endpoints**: No connections to live payer clearinghouses, insurance gateways, or hospital EHR systems.
- **Local Execution**: All data generation, validation, and analytics operate entirely within local synthetic database environments.

---

## 📄 License & Portfolio Notice

This project is created for educational and portfolio demonstration purposes, showcasing enterprise data operations, healthcare RCM analysis, SQL quality assurance engineering, and relational architecture.

---

**ClaimIQ** — *Healthcare Claims Data Quality & Operations Platform*

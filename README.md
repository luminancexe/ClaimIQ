# ClaimIQ

### Healthcare Claims Data Quality & Operations Platform

ClaimIQ is a synthetic-data healthcare Revenue Cycle Management (RCM) data quality and operations platform designed to identify claims-data discrepancies, validate operational workflows, support issue investigation, and provide actionable analytics and reporting.

The project is being developed as a phased software engineering project, with a strong focus on **SQL, MySQL 8.x, data quality, quality assurance, data integrity, operational analytics, documentation, and AI-assisted investigation**.

> **Important:** ClaimIQ uses synthetic healthcare data exclusively. It does not process real patient information, Protected Health Information (PHI), real insurance records, real claims, or production healthcare systems.

---

## 🎯 Project Mission

Healthcare Revenue Cycle Management depends on large volumes of interconnected operational and financial data. Even relatively small data inconsistencies can result in incorrect reporting, payment discrepancies, unresolved claims, and downstream operational issues.

ClaimIQ aims to simulate a data operations environment where analysts can:

- Validate healthcare claims data
- Detect data-quality issues
- Identify financial discrepancies
- Detect invalid relationships and business-rule violations
- Investigate operational issues
- Track issue resolution
- Monitor data-quality metrics
- Generate operational reports
- Maintain QA rules and process documentation
- Use AI to assist with investigation and explanation of verified issues

The goal is not to recreate a production healthcare billing system, but to demonstrate how a data operations platform can maintain **accuracy, consistency, traceability, and operational quality** across a claims dataset.

---

## 🏥 RCM Domain

ClaimIQ models a simplified healthcare Revenue Cycle Management lifecycle:

```text
Patient
   ↓
Encounter
   ↓
Claim Creation
   ↓
Claim Submission
   ↓
Payer Processing
   ↓
Adjudication
   ├── Accepted
   ├── Rejected
   └── Denied
   ↓
Payment / Adjustment
   ↓
Remittance
   ↓
Reconciliation
   ↓
Resolution
```

The platform uses synthetic representations of common RCM concepts including:

- Patients
- Providers
- Healthcare organizations
- Payers and insurance plans
- Encounters
- Procedures
- Claims
- Claim lines
- Payments
- Adjustments
- Denials
- Remittances
- Claim statuses
- Reconciliation records

Healthcare coding and transaction concepts may be modeled using synthetic equivalents inspired by industry terminology. No real patient, payer, or billing data is used.

---

## 🔎 Problems ClaimIQ Addresses

ClaimIQ focuses on five major categories of operational data problems.

### 1. Data Quality

- Missing mandatory fields
- Duplicate records
- Invalid identifiers
- Malformed values
- Inconsistent data

### 2. Financial Discrepancies

- Payment greater than claim amount
- Negative financial values
- Duplicate payments
- Incorrect adjustments
- Unreconciled balances

### 3. Temporal Anomalies

- Submission before service
- Payment before submission
- Denial before submission
- Future-dated events
- Invalid event sequences

### 4. Referential Integrity

- Orphaned claims
- Invalid patient references
- Invalid provider references
- Invalid payer references
- Payments referencing nonexistent claims

### 5. Business Logic Violations

Examples include:

- Paid claim with zero payment
- Denied claim with positive payment
- Pending claim with payment
- Claims without service lines
- Invalid claim-status combinations

---

## 🧩 Core Capabilities

The completed ClaimIQ platform is planned to provide:

### Data Quality

- Automated QA validation
- Data-quality scoring
- Duplicate detection
- Missing-data detection
- Referential integrity validation
- Financial validation
- Business-rule validation

### Claims Operations

- Claims search
- Claims exploration
- Claim lifecycle tracking
- Issue investigation
- Issue assignment
- Resolution tracking
- Escalation workflows

### Analytics

- Data-quality trends
- Issue distribution
- Provider-level analysis
- Payer-level analysis
- Financial discrepancy analysis
- Claims status analysis
- QA rule performance

### Reporting

- Daily Data Quality Reports
- Weekly Operations Reports
- Critical Financial Discrepancy Reports
- Provider Quality Scorecards
- Payer Reports
- Claims Pipeline Reports
- QA Performance Reports

### AI-Assisted Operations

The final phase will introduce an AI assistant capable of working with verified ClaimIQ data to assist with:

- Issue explanations
- Investigation summaries
- Operational report generation
- Pattern analysis
- SOP guidance

The AI layer is designed to **explain and assist with verified data rather than act as the source of truth**.

---

# 🏗️ Project Architecture

ClaimIQ is being developed incrementally.

```text
                    ┌─────────────────────┐
                    │     ClaimIQ UI      │
                    │     Dashboard       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Backend API     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Claims Services    QA Engine        Reporting
              │                │                │
              │                ▼                │
              │          SQL Validation         │
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │      Database       │
                    └──────────┬──────────┘
                               │
                               ▼
                    Synthetic Data Engine
                               │
                               ▼
                       Error Injection
                               │
                               ▼
                      Controlled QA Tests
```

The architecture will evolve throughout the project's phases.

---

# 🛠️ Planned Technology Stack

The technology stack will be finalized during the relevant implementation phases.

| Area | Technology |
|---|---|
| Database | MySQL 8.x (Storage Engine: InnoDB, Charset: utf8mb4) |
| Financial Precision | DECIMAL(12,2) with Exact Fixed-Point String Math |
| Temporal Standard | DATETIME(6), UTC |
| Querying | SQL / Parameterized Queries |
| Data Generation | Python 3.10+ (Faker, Deterministic Seeds) |
| Data Analysis | Python (Analytics Engine, Pareto 80/20, Recurrence) |
| Backend | FastAPI (Python 3.10+, Pydantic v2, PyJWT, Uvicorn) |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Visualization | Recharts 2.x (Donuts, Trends, Pareto Curves, Score Bars) |
| State & Cache | TanStack React Query 5.x |
| Testing | pytest (Backend: 158 tests) + Vitest & RTL (Frontend: 29 tests) |
| Architecture | Decoupled REST SPA with Strict Read-Only Database Invariant |


---

# 📋 Project Roadmap

ClaimIQ is divided into 12 major phases.

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Domain Research, Scope & Requirements | ✅ Complete |
| **Phase 2** | Database Architecture & Data Modeling | ✅ Complete |
| **Phase 3** | Synthetic Data Generation | ✅ Complete |
| **Phase 4** | Controlled Data Error Injection | ✅ Complete |
| **Phase 5** | SQL Data Quality Engine | ✅ Complete |
| **Phase 6** | Python Analytics Engine | ✅ Complete |
| **Phase 7** | Backend & API | ✅ Complete |
| **Phase 8** | Operations Dashboard | ✅ Complete |
| **Phase 9** | Investigation, Audit & Reporting | 🔜 Next |
| **Phase 10** | SOP & Documentation System | ⏳ Planned |

| **Phase 11** | Testing, Security & Performance | ⏳ Planned |
| **Phase 12** | AI Intelligence & Final Release | ⏳ Planned |

---

# 📚 Phase 1 — Requirements Foundation

Phase 1 established the conceptual and operational foundation of ClaimIQ.

Documentation includes:

```text
docs/
├── project-overview.md
├── rcm-domain-overview.md
├── problem-definition.md
├── users-and-roles.md
├── use-cases.md
├── functional-requirements.md
├── non-functional-requirements.md
├── data-quality-framework.md
├── severity-model.md
├── claim-lifecycle.md
├── issue-lifecycle.md
├── operational-workflow.md
├── reporting-requirements.md
├── success-metrics.md
├── project-scope.md
└── requirements-traceability-matrix.md

reports/
└── PHASE_1_COMPLETION_REPORT.md
```

Phase 1 established:

- 16 formal use cases
- 60+ functional requirements
- Non-functional requirements
- Seven data-quality dimensions
- Claim lifecycle model
- Issue lifecycle model
- Severity framework
- Operational workflow
- Reporting requirements
- Success metrics
- Requirements traceability
- Project scope and phase dependencies

### Phase 1 Status

**Complete and verified.**

No database, backend, frontend, AI implementation, or production infrastructure was introduced during Phase 1.

---

# 🏛️ Phase 2 — Database Architecture & Data Modeling

Phase 2 established the complete MySQL 8.x relational foundation for ClaimIQ.

Documentation and schema artifacts include:

```text
docs/
├── database-architecture.md
├── entity-relationship-diagram.md
├── data-dictionary.md
├── normalization-strategy.md
├── index-strategy.md
├── database-conventions.md
├── claim-data-model.md
└── phase-2-schema-validation.md

database/
├── schema/
│   ├── 01_reference_tables.sql
│   ├── 02_patient_provider_tables.sql
│   ├── 03_clinical_encounter_tables.sql
│   ├── 04_claims_tables.sql
│   ├── 05_financial_tables.sql
│   ├── 06_operations_qa_tables.sql
│   ├── 07_audit_tables.sql
│   ├── 08_indexes.sql
│   └── 09_seed_reference_data.sql
│
├── migrations/
│   └── 001_initial_schema.sql
│
└── validate_schema.py

reports/
└── PHASE_2_COMPLETION_REPORT.md
```

Phase 2 established:
- MySQL 8.x database architecture with InnoDB storage engine and utf8mb4 character set
- Standardized temporal precision (`DATETIME(6)` in UTC) and exact financial precision (`DECIMAL(12,2)`)
- 22 normalized tables and 124 documented columns
- Primary keys (`BIGINT UNSIGNED AUTO_INCREMENT`) and foreign keys with declarative referential integrity
- Unique, NOT NULL, and CHECK constraints
- Secondary B-Tree index strategy for foreign keys and operational queues
- Claim lifecycle and state transition history model
- Financial reconciliation and variance balancing model
- Operational issue management and root-cause tracking model
- QA engine metadata and execution telemetry supporting structures
- Immutable audit event logging structure
- Deterministic, reproducible migration script (`001_initial_schema.sql`)
- MySQL 8.x Python schema validation harness (`validate_schema.py`)

### Phase 2 Status

**Complete and verified.**

The schema contains the structural foundation and reference data, but no large synthetic datasets, error injection, or QA engine implementation.

---

# ⚙️ Phase 3 — Synthetic Data Generation Engine

Phase 3 implemented the deterministic synthetic healthcare data generation engine and produced a 100% clean, mathematically balanced baseline dataset in MySQL 8.x.

Documentation and generation modules include:

```text
docs/
├── phase-3-data-generation.md
├── synthetic-data-model.md
├── generation-configuration.md
├── clinical-code-library.md
├── generation-validation.md
└── generation-performance.md

generator/
├── config.py
├── database.py
├── random_state.py
├── identifiers.py
├── dates.py
├── financials.py
├── distributions.py
├── reference_data.py
├── validators.py
├── cli.py
├── templates/
└── generators/

tests/
├── test_identifiers.py
├── test_dates.py
├── test_financials.py
├── test_distributions.py
└── test_generation.py

reports/
└── PHASE_3_COMPLETION_REPORT.md
```

Phase 3 established:

- Deterministic multi-scale synthetic generation (`small`: 1k claims, `medium`: 10k claims, `large`: 100k claims)
- Seeded reproducibility (`random.Random(seed)` + `Faker.seed(seed)`)
- Standardized 10-digit NPI generation with CMS Luhn checksum validation
- 35 CPT procedural codes and 45 ICD-10 diagnostic codes in a controlled clinical code library
- Exact `Decimal(12, 2)` fixed-point arithmetic ensuring $\text{Variance} = \$0.00$ on all baseline reconciliations
- Strict chronological date sequencing adhering to payer timely filing limits
- Realistic claim lifecycle state transition tracking (`Submitted` $\rightarrow$ `Accepted` $\rightarrow$ `Paid` / `Partially Paid` / `Denied`)
- Chunked batch database insertion (`2,500` rows per chunk) with active foreign keys
- Automated 7-dimension SQL data quality validation suite (`python -m generator --validate`)
- Safe database reset mechanism (`python -m generator --reset`) preserving schema and reference data

### Phase 3 Status

**Complete and verified.**

The generated dataset represents a clean operational baseline ready for Phase 4 controlled error injection.

---

# 💉 Phase 4 — Controlled Error Injection & Anomaly Datasets

Phase 4 implemented the deterministic error injection framework capable of creating controlled, realistic, traceable defects in copies of the clean Phase 3 baseline dataset.

Documentation and injection modules include:

```text
docs/
├── phase-4-error-injection.md
├── anomaly-taxonomy.md
├── injection-profiles.md
├── anomaly-ground-truth.md
├── anomaly-validation.md
└── phase-4-test-results.md

database/schema/
└── 10_ground_truth_tables.sql

generator/
├── inject.py
└── injector/
    ├── models.py
    ├── taxonomy.py
    ├── profiles.py
    ├── engine.py
    ├── ground_truth.py
    ├── validators.py
    ├── cli.py
    └── mutators/
        ├── completeness.py
        ├── duplication.py
        ├── referential.py
        ├── financial.py
        ├── temporal.py
        ├── lifecycle.py
        ├── business_logic.py
        └── formatting.py

tests/
├── test_anomaly_selection.py
├── test_anomaly_determinism.py
├── test_financial_anomalies.py
├── test_temporal_anomalies.py
├── test_duplicate_anomalies.py
├── test_lifecycle_anomalies.py
├── test_ground_truth.py
├── test_reset.py
└── test_injection_profiles.py

reports/
└── PHASE_4_COMPLETION_REPORT.md
```

Phase 4 established:

- Authoritative **67-anomaly taxonomy** (`E001`–`E067`) spanning all 8 core defect categories
- Deterministic multi-scale injection profiles (`clean`, `light`: ~1%, `moderate`: ~5%, `heavy`: ~10%, `targeted`)
- Explicit **Ground Truth Registry** (`anomaly_ground_truth` table in MySQL 8.x + JSON export)
- Dry-run simulation mode (`python -m generator.inject --profile moderate --seed 42 --dry-run`)
- Targeted anomaly injection CLI (`python -m generator.inject --profile targeted --anomaly E023,E030,E034`)
- Automated anomaly validation suite auditing live database state against ground truth
- Precise two-way mutation reversion (`python -m generator.inject --reset-anomalies`)
- Comprehensive test suite (41 unit & regression tests passing in 0.57s)

### Phase 4 Status

**Complete and verified.**

The anomalous datasets and ground truth registry are ready for Phase 5 automated QA rule evaluation.

---

# 🔍 Phase 5 — Data Quality & QA Rule Engine

Phase 5 implemented the database-backed SQL validation and QA rule execution engine.

Documentation and engine modules include:

```text
docs/
├── phase-5-qa-engine.md
├── qa-rule-catalog.md
├── qa-execution.md
├── qa-scoring.md
├── qa-ground-truth-evaluation.md
├── qa-validation.md
└── phase-5-test-results.md

qa/
├── __init__.py
├── __main__.py
├── config.py
├── models.py
├── registry.py
├── database.py
├── scoring.py
├── ground_truth.py
├── validators.py
├── engine.py
├── cli.py
└── rules/
    ├── completeness.py
    ├── duplication.py
    ├── referential.py
    ├── financial.py
    ├── temporal.py
    ├── lifecycle.py
    ├── business_logic.py
    └── formatting.py

tests/
├── test_qa_registry.py
├── test_qa_rules.py
├── test_qa_financial.py
├── test_qa_temporal.py
├── test_qa_lifecycle.py
├── test_qa_ground_truth.py
├── test_qa_scoring.py
├── test_qa_determinism.py
└── test_qa_integration.py

reports/
└── PHASE_5_COMPLETION_REPORT.md
```

Phase 5 established:

- **67-rule QA catalog** (`R-E001`–`R-E067`) mapped to all 7 Data Quality dimensions
- SQL-first anomaly detection with specialized algorithm validators (CMS Luhn NPI checksum)
- 7-dimension weighted Data Quality Scoring formula producing aggregate scores $[0.0, 100.0]$
- Ground truth accuracy evaluator calculating True Positives, False Positives, False Negatives, Precision ($100\%$), Recall ($100\%$), and F1 ($1.0000$)
- Telemetry persistence into `qa_execution_runs`, `qa_results`, and `issues`
- Clean baseline validation verifying zero unexpected defects on uncorrupted datasets
- Comprehensive test suite (68 unit & integration tests passing in 0.58s)

### Phase 5 Status

**Complete and verified.**

The QA rule engine, execution telemetry logs, and dimensional scoring algorithms are ready for Phase 6 analytical metric aggregation.

---

# 📊 Phase 6 — Python Analytics Engine & Advanced Data Quality Analytics

Phase 6 implemented the deterministic, database-aware Python analytical calculation engine.

Documentation, analytics modules, and tests include:

```text
docs/
├── phase-6-analytics-engine.md
├── analytics-financial.md
├── analytics-kpis.md
├── analytics-scorecards.md
├── analytics-trends.md
├── analytics-root-cause.md
├── analytics-recurrence.md
├── analytics-validation.md
└── phase-6-test-results.md

analytics/
├── __init__.py
├── __main__.py
├── config.py
├── models.py
├── database.py
├── financial.py
├── kpis.py
├── scorecards.py
├── trends.py
├── root_cause.py
├── recurrence.py
├── engine.py
└── cli.py

tests/
├── test_analytics_financial.py
├── test_analytics_kpis.py
├── test_analytics_scorecards.py
├── test_analytics_trends.py
├── test_analytics_root_cause.py
├── test_analytics_recurrence.py
├── test_analytics_determinism.py
├── test_analytics_engine.py
└── test_analytics_integration.py

reports/
└── PHASE_6_COMPLETION_REPORT.md
```

Phase 6 established:

- **Financial Exposure Analytics**: Exact fixed-point `Decimal` arithmetic enforcing $Billed = Paid + Contractual + PatientResp$, overpayment calculations, and reconciliation rates.
- **Operational KPI Rollups**: Claims volume & status distributions, payment turnaround velocity, denial rates, defect density, and clean record rate.
- **Provider & Payer Scorecards**: Safe SQL attribution preventing Cartesian row multiplication, tracking collection efficiency, timely filing compliance, and DQ scores.
- **Longitudinal DQ Trends**: Daily, weekly, and monthly time-series score tracking with velocity calculations and trajectory classification (`IMPROVING`, `STABLE`, `DEGRADING`).
- **Pareto 80/20 Root-Cause Analysis**: Algorithmic defect concentration ranking identifying the vital few anomaly codes driving 80% of data quality issues.
- **Recurrence Pattern Clustering**: Detection of repeat offenders ($\ge 2$ occurrences) across providers, payers, and rules.
- **Deterministic CLI Reporting**: `python -m analytics --report overview/financial/kpis/provider/payer/trends/root-cause/recurrence/all` with dry-run and JSON export support.
- **Comprehensive Test Suite**: 104 tests passing across the entire ClaimIQ suite in <1.0s.

### Phase 6 Status

**Complete and verified.**

The analytics layer is ready for Phase 7 Backend & REST API consumption.

---

# 🚀 Phase 7 — Backend & API

Phase 7 delivered a complete, production-grade **FastAPI REST API** exposing all Phase 1–6 functionality through a secure service boundary:

```text
backend/
├── __init__.py           # Exports create_app() application factory
├── __main__.py           # Uvicorn entrypoint (python -m backend)
├── app.py                # FastAPI application factory & router mounting
├── config.py             # BackendConfig dataclass with environment parsing
├── database.py           # Read-only MySQL connection helpers
├── dependencies.py       # FastAPI Depends() helpers (get_db, get_current_user, require_role)
├── schemas/              # Pydantic v2 request/response models
│   ├── common.py         # PaginatedResponse[T], ErrorResponse, HealthResponse
│   ├── auth.py           # LoginRequest, TokenResponse, RefreshRequest, UserProfile
│   ├── claims.py         # ClaimSummary, ClaimDetail, ClaimLineSchema, StatusHistoryEntry
│   ├── qa.py             # QARuleSchema, QARunSchema, QAResultSchema, DQScoreSchema
│   ├── analytics.py      # FinancialOverview, KPIResponse, TrendResponse, Scorecards
│   └── issues.py         # IssueSummary, IssueDetail
├── services/             # Pure service layer delegating to existing engines
│   ├── auth.py           # PBKDF2 hashing, JWT signing/verification, user store
│   ├── claims.py         # Parameterized read-only claims queries
│   ├── qa.py             # Delegation to qa.registry, qa.engine, qa.scoring
│   ├── analytics.py      # Delegation to analytics.engine and calculations
│   └── issues.py         # Parameterized read-only issue inspection
├── routers/              # HTTP endpoint handlers with OpenAPI documentation
│   ├── health.py         # /health and /api/v1/health
│   ├── auth.py           # /api/v1/auth (login, refresh, me)
│   ├── claims.py         # /api/v1/claims
│   ├── qa.py             # /api/v1/qa (rules, runs, results, scores, issues)
│   ├── analytics.py      # /api/v1/analytics (overview, financial, kpis, trends, ...)
│   ├── providers.py      # /api/v1/providers
│   ├── payers.py         # /api/v1/payers
│   └── issues.py         # /api/v1/issues
└── middleware/           # Cross-cutting HTTP middleware
    ├── auth.py           # Token extraction helper
    └── errors.py         # Global RequestIdMiddleware & sensitive leak sanitizer
```

### Key Deliverables:
- **34 REST Endpoints**: Health, Auth, Claims, QA Rules/Runs/Results/Scores, Analytics Overview/Financial/KPIs/Trends/Root-Causes/Recurrence, Providers, Payers, and Issues.
- **JWT Authentication & RBAC**: HS256 JWT tokens with access & refresh token lifecycle, PBKDF2 password hashing, and role enforcement (`ADMIN`, `ANALYST`, `QA_REVIEWER`, `VIEWER`).
- **Read-Only Database Enforcement**: `SET SESSION TRANSACTION READ ONLY` on all connections.
- **Deterministic Bounded Pagination**: `PaginatedResponse[T]` with strict `page_size <= 500` limit.
- **Zero Information Leaks**: Standardized `ErrorResponse` suppressing stack traces and SQL statements.
- **Automated Test Suite**: 158 tests passing across the repository with 100% pass rate.

### Phase 7 Status

**Complete and verified.**

The API layer is ready for Phase 8 Operations Dashboard consumption.

---

# 🖥️ Phase 8 — Operations Dashboard

Phase 8 delivered a production-ready, dark cinematic **React + TypeScript** operations and analytics dashboard consuming all 34 endpoints from the Phase 7 FastAPI REST API.

Documentation and frontend modules include:

```text
docs/
├── phase-8-frontend.md
├── frontend-architecture.md
├── frontend-authentication.md
├── frontend-api-integration.md
├── frontend-responsive-design.md
└── frontend-testing.md

frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── src/
    ├── api/           # Centralized typed API client with JWT refresh & retry
    ├── types/         # Strict TypeScript models mirroring Pydantic schemas
    ├── context/       # AuthContext with auto-refresh & ProtectedRoute
    ├── components/    # AppShell, Header, Sidebar, MetricCard, DataTable, Charts, Filters
    ├── features/      # 12 Operational feature pages (Dashboard, Claims, QA, Analytics, ...)
    ├── utils/         # formatCurrency, formatPercentage, formatNumber, formatDate
    └── __tests__/     # 10 Vitest test suites (29 tests passing)

reports/
└── PHASE_8_COMPLETION_REPORT.md
```

### Key Deliverables:
- **Executive Operations Dashboard (`/dashboard`)**: 8 KPI metric cards, 7-dimension Data Quality score comparison, claim lifecycle status donut, financial reconciliation breakdown, longitudinal quality trend curves, and top Pareto defect drivers.
- **Relational Claims Explorer (`/claims`, `/claims/:id`)**: Server-paginated claims explorer with status/search filtering, detail view with financial rollups, itemized CPT procedure lines, and chronological lifecycle status history.
- **QA Observatory (`/qa/rules`, `/qa/runs`, `/qa/scores`)**: Complete catalog of all 67 QA validation rules (category & dimension filters), paginated execution runs history, per-rule telemetry duration metrics, and 7-dimension scorecard breakdown.
- **Analytics Suite (`/analytics/*`)**: Dedicated dashboards for Financial reconciliation discrepancies, operational KPIs, longitudinal quality trends (Daily/Weekly/Monthly), Pareto 80/20 root-cause defect rankings, and entity repeat offender clusters.
- **Provider & Payer Scorecards (`/providers/*`, `/payers/*`)**: Directory and detailed scorecards for provider quality and payer adjudication latency, payment turnaround velocity, and timely filing compliance.
- **Read-Only Defect Explorer (`/issues`, `/issues/:id`)**: Strictly observational defect inspection isolating Phase 9+ investigation and resolution workflows.
- **Authentication & RBAC**: Dual-token JWT lifecycle with silent refresh on 401, role-aware route guards (`ADMIN`, `ANALYST`, `QA_REVIEWER`, `VIEWER`), and quick-access dev login accounts.
- **Multi-Viewport Responsive Design**: Adaptive layouts verified across 5 breakpoints (`375px`, `768px`, `1024px`, `1440px`, `1920px`).
- **Comprehensive Automated Testing**: 29 frontend tests passing in Vitest (100% pass rate) + 158 backend tests passing in pytest.

### Quickstart & Running ClaimIQ

1. **Start Backend Server**:
   ```bash
   python -m backend
   # API: http://localhost:8000/api/v1
   # Swagger UI: http://localhost:8000/docs
   ```

2. **Start Frontend Dashboard**:
   ```bash
   cd frontend
   npm run dev
   # Dashboard: http://localhost:3000
   ```

### Phase 8 Status

**Complete and verified.**

---

# 🔐 Data & Privacy


ClaimIQ is intentionally designed around synthetic data.

The project will not contain:

- Real patient information
- Protected Health Information (PHI)
- Real medical records
- Real insurance member information
- Real claims
- Real payment transactions
- Production payer connections
- Production EHR integrations

All patient identifiers, provider identifiers, payer information, financial values, claims, procedures, and transactions will be generated synthetically.

---

# 🎯 Project Goals

The primary technical goals of ClaimIQ are to demonstrate:

- SQL proficiency
- Relational data modeling
- Data-quality engineering
- Data validation
- Data analysis
- QA methodology
- Root-cause investigation
- Operational workflow design
- Reporting
- Documentation
- API development
- Software testing
- Security fundamentals
- Performance analysis
- AI-assisted data operations

The project is specifically designed to demonstrate practical skills relevant to **Data Operations, RCM Operations, QA, Data Analysis, and AI-enabled operational systems**.

---

# ⚠️ Project Scope

ClaimIQ is an educational and portfolio project.

It is **not**:

- An EHR
- A medical diagnosis platform
- A clinical decision-support system
- A production claims processor
- A real insurance platform
- A real payer gateway
- A medical billing service
- A replacement for healthcare infrastructure

No clinical decisions should be made using ClaimIQ.

---

# 🧪 Development Philosophy

ClaimIQ follows a phased development and verification approach.

Each phase must:

1. Define a clear objective
2. Establish explicit deliverables
3. Remain within its defined scope
4. Validate its outputs
5. Produce a completion report
6. Establish readiness for the next phase

Features belonging to later phases should not be prematurely implemented.

This ensures that the project evolves from:

```text
Requirements
     ↓
Architecture
     ↓
    Data
     ↓
Validation
     ↓
Analytics
     ↓
Application
     ↓
Operations
     ↓
    AI
```

rather than attempting to build the entire platform simultaneously.

---

# 📈 Long-Term Vision

The final ClaimIQ platform will provide a simulated end-to-end environment for healthcare claims data operations:

```text
Synthetic Claims Data
        ↓
    Database
        ↓
  Automated QA
        ↓
Data Quality Analysis
        ↓
 Issue Detection
        ↓
 Investigation
        ↓
Resolution / Escalation
        ↓
Operational Reporting
        ↓
Trend Monitoring
        ↓
AI-Assisted Analysis
```

The ultimate objective is to demonstrate how **data quality, operational processes, analytics, and AI can work together to improve the reliability of complex claims workflows.**

---

# 📄 License

This project is intended for educational and portfolio purposes.

License information will be added as the project progresses.

---

## Project Status

- **Phase 1 — Domain Research, Scope & Requirements Definition:** ✅ Complete
- **Phase 2 — Database Architecture & Data Modeling:** ✅ Complete
- **Phase 3 — Synthetic Healthcare Claims Data Generation:** ✅ Complete
- **Phase 4 — Controlled Error Injection & Anomaly Dataset Engineering:** ✅ Complete
- **Phase 5 — Data Quality & QA Rule Engine:** ✅ Complete
- **Phase 6 — Python Analytics Engine & Advanced DQ Aggregation:** ✅ Complete
- **Phase 7 — Backend & API (FastAPI REST Service Layer):** ✅ Complete
- **Phase 8 — Operations Dashboard (React + TypeScript Frontend):** ✅ Complete
- **Next Phase: Phase 9 — Investigation, Audit & Reporting** (🔜 Next)

---


**ClaimIQ**  
*Healthcare Claims Data Quality & Operations Platform*


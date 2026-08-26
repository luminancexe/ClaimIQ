# ClaimIQ Phase 7: Backend & API Architecture

## 1. Overview

ClaimIQ Phase 7 introduces a high-performance, asynchronous REST API layer built with **FastAPI** (v0.115+) and **Pydantic v2**, executing on **Uvicorn**.

The API provides a secure, read-only service boundary over the completed Phase 1–6 ClaimIQ architecture:
- **Phase 1**: Clinical & Financial Domain Model
- **Phase 2**: MySQL 8.x Relational Schema (30 tables)
- **Phase 3**: Deterministic Synthetic Claims Generator
- **Phase 4**: Controlled Error Injection Engine (67 anomaly types)
- **Phase 5**: SQL Data Quality Engine (67 QA rules)
- **Phase 6**: Python Analytics Engine (Financial, KPIs, Scorecards, Trends, Root Cause, Recurrence)

```
+-------------------------------------------------------------------------+
|                              CLIENT APPS                                |
|             (Operations Dashboard / CLI / Swagger / REST)               |
+-------------------------------------------------------------------------+
                                    |
                                    | HTTP / JSON (Bearer JWT)
                                    v
+-------------------------------------------------------------------------+
|                         ClaimIQ FastAPI Backend                         |
|                                                                         |
|  +-------------------+  +---------------------+  +-------------------+  |
|  | RequestId M/ware  |  |   CORS Middleware   |  | Error Handler M/w |  |
|  +-------------------+  +---------------------+  +-------------------+  |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |                            ROUTERS                                |  |
|  |  /health  |  /auth  |  /claims  |  /qa  |  /analytics  | /issues  |  |
|  +-------------------------------------------------------------------+  |
|                                    |                                    |
|                                    v                                    |
|  +-------------------------------------------------------------------+  |
|  |                         SERVICE LAYER                             |  |
|  |  auth.py  |  claims.py  |  qa.py  |  analytics.py  |  issues.py   |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
          |                         |                        |
          | Read-Only SQL           | Registry / Rules       | Analytical Models
          v                         v                        v
+-------------------+     +-------------------+    +----------------------+
|  MySQL 8.x Schema |     | Phase 5 QA Engine |    | Phase 6 Analytics    |
| (SET READ ONLY)   |     | (67 Active Rules) |    | (Financial/KPI/Score)|
+-------------------+     +-------------------+    +----------------------+
```

---

## 2. Package Architecture

```
backend/
├── __init__.py           # Exports create_app() application factory
├── __main__.py           # Uvicorn runner entrypoint (python -m backend)
├── app.py                # FastAPI application factory and router mounting
├── config.py             # BackendConfig dataclass with environment parsing
├── database.py           # Read-only MySQL connection helpers
├── dependencies.py       # FastAPI Depends() helpers (get_db, get_current_user, require_role)
│
├── schemas/              # Pydantic v2 request/response models
│   ├── __init__.py
│   ├── common.py         # PaginatedResponse[T], ErrorResponse, HealthResponse
│   ├── auth.py           # LoginRequest, TokenResponse, RefreshRequest, UserProfile
│   ├── claims.py         # ClaimSummary, ClaimDetail, ClaimLineSchema, StatusHistoryEntry
│   ├── qa.py             # QARuleSchema, QARunSchema, QAResultSchema, DQScoreSchema
│   ├── analytics.py      # FinancialOverview, KPIResponse, TrendResponse, Scorecards
│   └── issues.py         # IssueSummary, IssueDetail
│
├── services/             # Pure service layer delegating to existing engines
│   ├── __init__.py
│   ├── auth.py           # PBKDF2 hashing, JWT signing/verification, user store
│   ├── claims.py         # Parameterized read-only claims queries
│   ├── qa.py             # Delegation to qa.registry, qa.engine, qa.scoring
│   ├── analytics.py      # Delegation to analytics.engine and calculations
│   └── issues.py         # Parameterized read-only issue inspection
│
├── routers/              # HTTP endpoint handlers with OpenAPI documentation
│   ├── __init__.py
│   ├── health.py         # /health and /api/v1/health
│   ├── auth.py           # /api/v1/auth (login, refresh, me)
│   ├── claims.py         # /api/v1/claims
│   ├── qa.py             # /api/v1/qa (rules, runs, results, scores, issues)
│   ├── analytics.py      # /api/v1/analytics (overview, financial, kpis, trends, ...)
│   ├── providers.py      # /api/v1/providers
│   ├── payers.py         # /api/v1/payers
│   └── issues.py         # /api/v1/issues
│
└── middleware/           # Cross-cutting HTTP middleware
    ├── __init__.py
    ├── auth.py           # Token extraction helper
    └── errors.py         # Global RequestIdMiddleware & sensitive leak sanitizer
```

---

## 3. Key Design Principles

1. **Service Boundary Over Business Logic**: The backend does NOT duplicate QA rules, analytics algorithms, or financial formulas. It acts strictly as an API gateway delegating to Phase 5 and Phase 6 engines.
2. **Read-Only Database Enforcement**: Every database connection establishes `SET SESSION TRANSACTION READ ONLY` to guarantee transactional and operational safety.
3. **Decimal-Aware Serialization**: Monetary and precision fields (`DECIMAL(12,2)`) serialize as string representations to prevent IEEE 754 floating-point inaccuracies.
4. **Security & Information Leak Prevention**: Global exception handlers intercept database errors and unhandled exceptions, returning standardized JSON error payloads and suppressing stack traces, raw SQL queries, and internal file paths.
5. **Deterministic Request Tracking**: Every incoming and outgoing HTTP request is stamped with a unique `X-Request-ID` header.

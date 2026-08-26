# ClaimIQ REST API: Endpoint Reference Catalog

This catalog documents all endpoints provided by the ClaimIQ Phase 7 REST API at `/api/v1/`.

## 1. Health & Diagnostics

| Method | Path | Auth | Description | Response Schema |
|---|---|---|---|---|
| `GET` | `/health` | No | Root liveness & DB connectivity check | `HealthResponse` |
| `GET` | `/api/v1/health` | No | Versioned API liveness & readiness check | `HealthResponse` |

### Example Response:
```json
{
  "status": "healthy",
  "version": "0.7.0",
  "database_connected": true,
  "timestamp": "2026-08-26T12:00:00.000000Z"
}
```

---

## 2. Authentication (`/api/v1/auth`)

| Method | Path | Auth | Description | Request / Response |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/login` | No | Authenticate user credentials & issue JWTs | `LoginRequest` -> `TokenResponse` |
| `POST` | `/api/v1/auth/refresh` | No | Exchange refresh token for new access token | `RefreshRequest` -> `TokenResponse` |
| `GET` | `/api/v1/auth/me` | Bearer | Retrieve authenticated user profile | `UserProfile` |

### Default Development Accounts:
- `admin` / `Admin@123` (Role: `ADMIN`)
- `analyst` / `Analyst@123` (Role: `ANALYST`)
- `qa_reviewer` / `QaReviewer@123` (Role: `QA_REVIEWER`)
- `viewer` / `Viewer@123` (Role: `VIEWER`)

---

## 3. Claims Management (`/api/v1/claims`)

| Method | Path | Auth | Description | Query Parameters |
|---|---|---|---|---|
| `GET` | `/api/v1/claims` | Bearer | Paginated claims list | `page`, `page_size`, `status`, `claim_reference`, `payer_id`, `provider_id`, `patient_id`, `start_date`, `end_date`, `is_reconciled` |
| `GET` | `/api/v1/claims/{claim_id}` | Bearer | Full claim detail + financial rollup | Path `claim_id: int` |
| `GET` | `/api/v1/claims/{claim_id}/lines` | Bearer | Itemized claim line items | Path `claim_id: int` |
| `GET` | `/api/v1/claims/{claim_id}/history` | Bearer | Claim lifecycle status transition audit | Path `claim_id: int` |

---

## 4. QA Rule Engine (`/api/v1/qa`)

| Method | Path | Auth | Description | Query Parameters |
|---|---|---|---|---|
| `GET` | `/api/v1/qa/rules` | Bearer | Inventory of all 67 QA rule definitions | `category`, `dimension` |
| `GET` | `/api/v1/qa/rules/{rule_id}` | Bearer | Single rule definition by ID or code | Path `rule_id: str` (e.g. `R-E001`) |
| `GET` | `/api/v1/qa/runs` | Bearer | Paginated QA execution runs | `page`, `page_size` |
| `GET` | `/api/v1/qa/runs/{run_id}` | Bearer | Execution telemetry for specific QA run | Path `run_id: int` |
| `GET` | `/api/v1/qa/results` | Bearer | Per-rule evaluation results | `run_id: int` |
| `GET` | `/api/v1/qa/scores` | Bearer | 7-dimension weighted DQ scores | `run_id: int` (default latest) |
| `GET` | `/api/v1/qa/issues` | Bearer | Paginated QA-detected defect issues | `page`, `page_size`, `severity`, `dimension`, `status`, `rule_id`, `claim_id` |

---

## 5. Analytics Engine (`/api/v1/analytics`)

| Method | Path | Auth | Description | Query Parameters |
|---|---|---|---|---|
| `GET` | `/api/v1/analytics/overview` | Bearer | Combined overview (financial + KPIs + root cause) | None |
| `GET` | `/api/v1/analytics/financial` | Bearer | Financial exposure, variance, reconciliation | None |
| `GET` | `/api/v1/analytics/kpis` | Bearer | Operational KPIs (claims, payments, denials, QA) | None |
| `GET` | `/api/v1/analytics/providers` | Bearer | Provider quality & financial scorecards | None |
| `GET` | `/api/v1/analytics/providers/{id}` | Bearer | Single provider quality scorecard | Path `provider_id: int` |
| `GET` | `/api/v1/analytics/payers` | Bearer | Payer adjudication efficiency scorecards | None |
| `GET` | `/api/v1/analytics/payers/{id}` | Bearer | Single payer efficiency scorecard | Path `payer_id: int` |
| `GET` | `/api/v1/analytics/trends` | Bearer | Longitudinal Data Quality score time-series | `interval` (`daily`, `weekly`, `monthly`) |
| `GET` | `/api/v1/analytics/root-causes` | Bearer | Pareto 80/20 defect concentration analysis | None |
| `GET` | `/api/v1/analytics/recurrence` | Bearer | Repeat offender defect clustering | None |

---

## 6. Providers & Payers Directories

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/providers` | Bearer | Paginated directory of healthcare providers |
| `GET` | `/api/v1/providers/{id}` | Bearer | Single healthcare provider profile |
| `GET` | `/api/v1/providers/{id}/scorecard` | Bearer | Provider quality scorecard |
| `GET` | `/api/v1/payers` | Bearer | Paginated directory of insurance payers |
| `GET` | `/api/v1/payers/{id}` | Bearer | Single insurance payer profile |
| `GET` | `/api/v1/payers/{id}/scorecard` | Bearer | Payer adjudication scorecard |

---

## 7. Issues (`/api/v1/issues`)

| Method | Path | Auth | Description | Query Parameters |
|---|---|---|---|---|
| `GET` | `/api/v1/issues` | Bearer | Paginated defect issues list | `page`, `page_size`, `severity`, `dimension`, `status`, `rule_id`, `claim_id` |
| `GET` | `/api/v1/issues/{issue_id}` | Bearer | Full issue detail with rule metadata | Path `issue_id: int` |

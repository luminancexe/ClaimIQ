# Frontend API Integration

## 1. API Client Specification

All REST requests originate from the centralized client in `src/api/client.ts`.

### 1.1 Base Configuration
- Base URL is configured via `import.meta.env.VITE_API_BASE_URL` (defaults to `http://localhost:8000/api/v1`).
- All requests automatically append JSON headers (`Content-Type: application/json`, `Accept: application/json`).
- `X-Request-ID` response headers are preserved and mapped to frontend error panels.

---

## 2. Phase 7 Endpoint Mapping (34 Endpoints)

| Endpoint | Method | Frontend Module | Return Type |
|---|---|---|---|
| `/health` | GET | `api/client.ts` | `HealthResponse` |
| `/api/v1/health` | GET | `api/client.ts` | `HealthResponse` |
| `/auth/login` | POST | `api/auth.ts` | `TokenResponse` |
| `/auth/refresh` | POST | `api/auth.ts` | `TokenResponse` |
| `/auth/me` | GET | `api/auth.ts` | `UserProfile` |
| `/claims` | GET | `api/claims.ts` | `PaginatedResponse<ClaimSummary>` |
| `/claims/{id}` | GET | `api/claims.ts` | `ClaimDetail` |
| `/claims/{id}/lines` | GET | `api/claims.ts` | `ClaimLine[]` |
| `/claims/{id}/history` | GET | `api/claims.ts` | `StatusHistoryEntry[]` |
| `/qa/rules` | GET | `api/qa.ts` | `QARule[]` |
| `/qa/rules/{id}` | GET | `api/qa.ts` | `QARule` |
| `/qa/runs` | GET | `api/qa.ts` | `PaginatedResponse<QARun>` |
| `/qa/runs/{id}` | GET | `api/qa.ts` | `QARun` |
| `/qa/results` | GET | `api/qa.ts` | `QAResult[]` |
| `/qa/scores` | GET | `api/qa.ts` | `DQScoreSummary` |
| `/qa/issues` | GET | `api/qa.ts` | `PaginatedResponse<IssueSummary>` |
| `/analytics/overview` | GET | `api/analytics.ts` | `AnalyticsOverview` |
| `/analytics/financial` | GET | `api/analytics.ts` | `FinancialOverview` |
| `/analytics/kpis` | GET | `api/analytics.ts` | `KPIOverview` |
| `/analytics/providers` | GET | `api/analytics.ts` | `ProviderScorecard[]` |
| `/analytics/providers/{id}` | GET | `api/analytics.ts` | `ProviderScorecard` |
| `/analytics/payers` | GET | `api/analytics.ts` | `PayerScorecard[]` |
| `/analytics/payers/{id}` | GET | `api/analytics.ts` | `PayerScorecard` |
| `/analytics/trends` | GET | `api/analytics.ts` | `DQTrendsSummary` |
| `/analytics/root-causes` | GET | `api/analytics.ts` | `RootCauseResponse` |
| `/analytics/recurrence` | GET | `api/analytics.ts` | `RecurrenceResponse` |
| `/providers` | GET | `api/providers.ts` | `PaginatedResponse<ProviderDetail>` |
| `/providers/{id}` | GET | `api/providers.ts` | `ProviderDetail` |
| `/providers/{id}/scorecard` | GET | `api/providers.ts` | `ProviderScorecard` |
| `/payers` | GET | `api/payers.ts` | `PaginatedResponse<PayerDetail>` |
| `/payers/{id}` | GET | `api/payers.ts` | `PayerDetail` |
| `/payers/{id}/scorecard` | GET | `api/payers.ts` | `PayerScorecard` |
| `/issues` | GET | `api/issues.ts` | `PaginatedResponse<IssueSummary>` |
| `/issues/{id}` | GET | `api/issues.ts` | `IssueDetail` |

---

## 3. Error Handling & Sanitization

Backend errors are captured and normalized into `ApiError` instances containing:
- `status`: HTTP status code
- `errorCode`: Standardized error string (e.g. `UNAUTHORIZED`, `CLAIM_NOT_FOUND`)
- `message`: User-safe message
- `requestId`: Telemetry identifier for operator tracing

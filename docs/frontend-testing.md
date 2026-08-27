# Frontend Testing & Quality Verification

## 1. Testing Infrastructure

Frontend tests are powered by **Vitest** and **React Testing Library** under a headless **jsdom** environment.

### 1.1 Test Configuration
- Configuration file: `frontend/vite.config.ts`
- Setup file: `frontend/src/test/setup.ts` (ResizeObserver mock, matchMedia mock, localStorage lifecycle cleanup)

---

## 2. Test Suite Inventory

| Test Module | Path | Tests | Coverage Scope |
|---|---|---|---|
| **Format Utilities** | `src/__tests__/format.test.ts` | 4 | Currency decimal preservation, percentages, number formatting, dates |
| **API Client** | `src/__tests__/api_client.test.ts` | 3 | Authorization token injection, ApiError normalization, 401 refresh & retry |
| **Auth & Guards** | `src/__tests__/auth_context.test.tsx` | 2 | Login state, role checking (`hasRole`), `ProtectedRoute` role blocking |
| **UI Components** | `src/__tests__/components.test.tsx` | 6 | MetricCard, StatusBadge, SeverityBadge, DataTable, PaginationBar, ErrorAlert, EmptyState |
| **Dashboard View** | `src/__tests__/dashboard.test.tsx` | 1 | 8 KPI cards, 7-dimension score chart, status donut, trends, Pareto preview |
| **Claims Views** | `src/__tests__/claims.test.tsx` | 2 | ClaimsExplorer list, pagination, ClaimDetail metadata, itemized lines, status history |
| **QA Observatory** | `src/__tests__/qa.test.tsx` | 3 | 67-rule catalog, QARuns list, QARunDetail telemetry, 7-dimension score scorecard |
| **Analytics Suite** | `src/__tests__/analytics.test.tsx` | 4 | FinancialPage, KPIsPage, TrendsPage (daily/weekly/monthly), RootCausesPage (Pareto), RecurrencePage |
| **Scorecards Views** | `src/__tests__/scorecards.test.tsx` | 2 | Providers list, ProviderDetail scorecard, Payers list, PayerDetail scorecard |
| **Issues Explorer** | `src/__tests__/issues.test.tsx` | 2 | Observational listing, IssueDetail inspection, strict verification of zero mutation controls |

**Total Frontend Tests**: **29 passed** (100% pass rate in 5.48s).

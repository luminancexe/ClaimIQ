# Phase 8 — Frontend & Operations Dashboard

## 1. Executive Summary

Phase 8 introduces a production-ready, dark cinematic **React + TypeScript** operations console for the **ClaimIQ** platform. Built with Vite, Tailwind CSS, TanStack React Query, Lucide icons, and Recharts, the frontend provides real-time visibility into claims processing, data quality rule enforcement, financial reconciliation, provider/payer performance scorecards, and defect telemetry.

The frontend is strictly a **read-only consumer** of the Phase 7 FastAPI REST API (34 endpoints), adhering to ClaimIQ's architectural invariants:
- **Zero direct database access** from the client
- **Zero data mutations** (`SET SESSION TRANSACTION READ ONLY` backend invariant preserved)
- **Zero Phase 9/10/12 creep** (no issue assignment, no status transitions, no AI/LLMs)
- **High Decimal precision preservation** for all financial figures

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Framework** | React 18.3 + TypeScript 5.7 | Component architecture with strict typing |
| **Bundler & Tooling** | Vite 6.1 | Fast HMR development and optimized production builds |
| **Styling & Theme** | Tailwind CSS 3.4 + PostCSS | Dark cinematic control-room design system |
| **Data Fetching & Cache** | TanStack React Query 5.66 | Client-side query caching and lifecycle synchronization |
| **Routing & Navigation** | React Router 6.28 | Client-side SPA routing with protected role guards |
| **Visualizations** | Recharts 2.15 | Responsive charts (Donuts, Line Trends, Pareto Curves, Score Bars) |
| **Icons** | Lucide React 0.475 | Clean technical iconography |
| **Testing** | Vitest 3.0 + React Testing Library | Unit and component integration testing |

---

## 3. Directory Layout

```text
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── .env.example
│
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── router.tsx
    ├── index.css
    ├── vite-env.d.ts
    │
    ├── api/                  # Centralized typed API client
    │   ├── client.ts         # Axios/Fetch wrapper with JWT auto-refresh
    │   ├── auth.ts           # /api/v1/auth
    │   ├── claims.ts         # /api/v1/claims
    │   ├── qa.ts             # /api/v1/qa
    │   ├── analytics.ts      # /api/v1/analytics
    │   ├── providers.ts      # /api/v1/providers
    │   ├── payers.ts         # /api/v1/payers
    │   └── issues.ts         # /api/v1/issues
    │
    ├── types/                # Strict TypeScript contracts matching Phase 7
    │   ├── api.ts            # PaginatedResponse, ColumnDef, ErrorResponse
    │   ├── auth.ts           # LoginRequest, TokenResponse, UserProfile, UserRole
    │   ├── claims.ts         # ClaimSummary, ClaimDetail, ClaimLine, StatusHistoryEntry
    │   ├── qa.ts             # QARule, QARun, QAResult, DQScoreSummary
    │   ├── analytics.ts      # FinancialOverview, KPIOverview, Trends, RootCauses, Recurrence
    │   └── entities.ts       # ProviderDetail, PayerDetail, IssueSummary, IssueDetail
    │
    ├── context/
    │   └── AuthContext.tsx   # AuthProvider, ProtectedRoute, role checking
    │
    ├── components/
    │   ├── layout/           # AppShell, Header, Sidebar, Breadcrumbs
    │   ├── cards/            # MetricCard, StatusBadge, SeverityBadge, DimensionBadge, RoleBadge
    │   ├── tables/           # DataTable, PaginationBar
    │   ├── charts/           # TrendChart, StatusDonut, ParetoBarChart, DimensionBarChart, FinancialBreakdownChart
    │   ├── filters/          # FilterBar, SearchInput, SelectFilter
    │   └── feedback/         # LoadingSpinner, Skeleton, ErrorAlert, EmptyState
    │
    ├── features/             # Feature views & pages
    │   ├── auth/             # LoginPage
    │   ├── dashboard/        # DashboardPage
    │   ├── claims/           # ClaimsExplorerPage, ClaimDetailPage
    │   ├── qa/               # QAOverviewPage, QARulesPage, QARunsPage, QARunDetailPage, DQScoresPage
    │   ├── analytics/        # AnalyticsHubPage, FinancialPage, KPIsPage, TrendsPage, RootCausesPage, RecurrencePage
    │   ├── providers/        # ProvidersListPage, ProviderDetailPage
    │   ├── payers/           # PayersListPage, PayerDetailPage
    │   └── issues/           # IssuesListPage, IssueDetailPage (Read-Only)
    │
    ├── utils/                # formatCurrency, formatPercentage, formatNumber, formatDate
    └── constants/            # Role metadata, status colors, navigation links
```

---

## 4. Operational Views & Routes

| Route | View Component | Description |
|---|---|---|
| `/login` | `LoginPage` | Operator authentication with dev account quick selectors |
| `/dashboard` | `DashboardPage` | Executive console: Top 8 KPIs, 7-dimension score, status donut, trends, Pareto drivers |
| `/claims` | `ClaimsExplorerPage` | Server-paginated relational claims table with status and search filters |
| `/claims/:id` | `ClaimDetailPage` | Claim metadata, financial rollups, itemized CPT lines, and status history |
| `/qa` | `QAOverviewPage` | QA observatory hub with summary telemetry and quick links |
| `/qa/rules` | `QARulesPage` | Complete catalog of all 67 QA validation rules with category/dimension filters |
| `/qa/runs` | `QARunsPage` | Paginated QA execution batch runs history |
| `/qa/runs/:id` | `QARunDetailPage` | Execution telemetry with per-rule durations and detected issue counts |
| `/qa/scores` | `DQScoresPage` | Full 7-dimension scorecard with raw/weighted calculations and severity breakdown |
| `/analytics` | `AnalyticsHubPage` | Analytics navigation hub |
| `/analytics/financial` | `FinancialPage` | Financial reconciliation, contractual adjustments, and exposure metrics |
| `/analytics/kpis` | `KPIsPage` | Operational KPIs spanning volume, payment velocity, denials, and QA density |
| `/analytics/trends` | `TrendsPage` | Time-series trend analysis across Daily, Weekly, and Monthly intervals |
| `/analytics/root-causes` | `RootCausesPage` | Pareto 80/20 defect ranking with cumulative curve and financial exposure |
| `/analytics/recurrence` | `RecurrencePage` | Repeat defect clusters and repeat offender ranking |
| `/providers` | `ProvidersListPage` | Directory of providers with quality scores, volume, and denial rates |
| `/providers/:id` | `ProviderDetailPage` | Provider credentialing context and comprehensive performance scorecard |
| `/payers` | `PayersListPage` | Payer directory with adjudication latency, payment velocity, and filing compliance |
| `/payers/:id` | `PayerDetailPage` | Payer policy terms, filing limits, and operational scorecard |
| `/issues` | `IssuesListPage` | Read-only defect issues explorer with severity and dimension filters |
| `/issues/:id` | `IssueDetailPage` | Read-only issue inspection with rule context and variance amount |

---

## 5. Verification & Quality Gates

- **Unit & Component Testing**: 10 test suites, 29 tests passing (100% pass rate in Vitest).
- **Type Safety**: Strict TypeScript checking (`npx tsc --noEmit`) with 0 errors.
- **Production Build**: Optimized bundle built with Vite (`npm run build`) in 17.8s.
- **Backend Regression**: 158/158 pytest backend tests passing (100% pass rate).

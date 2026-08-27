# Frontend Architecture & Design System

## 1. Architectural Principles

The ClaimIQ frontend adheres to the following core architectural invariants:

1. **Strict Read-Only Consumer**: The frontend interacts with backend services exclusively through the Phase 7 FastAPI REST API. No direct database drivers or local SQL queries exist in the frontend layer.
2. **Separation of Concerns**:
   - `src/api/`: Handles network communication, headers, token attachment, auto-refresh, and error parsing.
   - `src/types/`: Defines TypeScript interfaces that mirror the backend Pydantic schemas 1:1.
   - `src/context/`: Manages authentication state, user identity, and session lifecycle.
   - `src/components/`: Houses reusable, presentational, and layout primitives.
   - `src/features/`: Contains domain-specific page views and orchestrates data queries.
   - `src/utils/`: Provides numerical, currency, date, and string formatting utilities.
3. **High-Precision Financial Handling**: All currency amounts are preserved as strings from the API and formatted via `formatCurrency()` using localized `Intl.NumberFormat` to prevent floating-point inaccuracy.

---

## 2. Visual Design System

The ClaimIQ interface employs a **dark cinematic operations-console** aesthetic designed for data density, high contrast, and minimal distraction.

### 2.1 Color Palette
- **Canvas / Background**: `#090d16` (Deep Slate / Midnight Navy)
- **Surfaces & Cards**: `#0f172a` (Slate 900) & `#1e293b` (Slate 800)
- **Borders & Dividers**: `#334155` (Slate 700 / 60% opacity)
- **Primary Accent**: `#06b6d4` (Cyan 500) with subtle glow shadows
- **Success / Optimal**: `#10b981` (Emerald 500)
- **Warning / Degraded**: `#f59e0b` (Amber 500)
- **Danger / Critical**: `#f43f5e` (Rose 500)
- **Secondary / Metric**: `#6366f1` (Indigo 500)

### 2.2 Typography
- **Primary Interface**: Inter / System Sans-Serif (`font-sans`)
- **Identifiers & Values**: JetBrains Mono / Fira Code (`font-mono`) for Claim References, NPIs, CPT codes, Rule IDs, and Currency figures.

---

## 3. Component Hierarchy

```text
App (QueryClientProvider, BrowserRouter, AuthProvider)
└── AppRouter
    ├── /login -> LoginPage
    └── ProtectedRoute (AppShell)
        ├── Header (Brand, Connectivity Indicator, User Badge, Logout)
        ├── Sidebar (Collapsible / Mobile Drawer, Nav Links, Role Guard)
        ├── Breadcrumbs (Path Navigation)
        └── Feature Page View
            ├── MetricCard Grid (Key performance indicators)
            ├── FilterBar (SearchInput, SelectFilter, DateFilter)
            ├── Visualizations (Recharts: Line, Bar, Donut, Pareto)
            ├── DataTable (Accessible, responsive, sortable columns)
            └── PaginationBar (Server-side page navigation controls)
```

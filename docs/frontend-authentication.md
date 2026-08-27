# Frontend Authentication & RBAC

## 1. Authentication Lifecycle

ClaimIQ implements a dual-token JWT authentication flow aligned with Phase 7 backend contracts.

### 1.1 Token Management
- **Access Token**: Short-lived JWT (60 minutes) stored in browser storage and injected into all outgoing HTTP requests via `Authorization: Bearer <access_token>`.
- **Refresh Token**: Long-lived JWT (1440 minutes / 24 hours) used to silently request new access tokens upon expiration without requiring operator re-authentication.

### 1.2 Silent Refresh Flow
```text
Client Request
      │
      ▼
HTTP 401 Unauthorized?
      ├── NO  ──> Process response
      │
      └── YES ──> Is a refresh already in flight?
                    ├── YES ──> Await shared refresh promise
                    └── NO  ──> POST /api/v1/auth/refresh { refresh_token }
                                  ├── Success: Store new tokens, retry original request
                                  └── Failure: Clear state, dispatch claimiq:auth:expired event, redirect to /login
```

---

## 2. Development Role-Based Access Control (RBAC)

The frontend recognizes the four canonical development roles:

| Role | Label | Permitted Feature Domains |
|---|---|---|
| `ADMIN` | Administrator | Full read access across all 7 operational modules |
| `ANALYST` | Data Analyst | Dashboard, Claims, Analytics Suite, Providers, Payers, Issues, QA |
| `QA_REVIEWER` | QA Reviewer | Dashboard, QA Observatory, Claims, Analytics, Issues |
| `VIEWER` | Read-Only Viewer | Dashboard, Claims, Providers, Payers, QA, Analytics, Issues |

### 2.1 UI Guards vs. Backend Boundary
- **`ProtectedRoute`**: Verifies user authentication before rendering the application shell.
- **`RoleGuard`**: Restricts navigation and component visibility based on the user's role.
- **Security Boundary**: Frontend guards are designed for operator UX and workflow clarity. The backend remains the authoritative security boundary with mandatory JWT role verification.

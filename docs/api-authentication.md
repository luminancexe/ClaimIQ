# ClaimIQ REST API: Authentication & Authorization Architecture

## 1. Overview

ClaimIQ Phase 7 implements a lightweight, cryptographically secure authentication and authorization subsystem using **JSON Web Tokens (JWT)** and **PBKDF2 password hashing**.

All protected routes require a valid JWT passed in the HTTP `Authorization` header:

```http
Authorization: Bearer <access_token>
```

---

## 2. Token Lifecycles & Configuration

| Parameter | Environment Variable | Default Value | Description |
|---|---|---|---|
| Signing Algorithm | Fixed | `HS256` | HMAC with SHA-256 |
| Access Expiration | `CLAIMIQ_JWT_EXPIRATION_MINUTES` | `60` min | Short-lived token for API operations |
| Refresh Expiration | `CLAIMIQ_JWT_REFRESH_EXPIRATION_MINUTES` | `1440` min (24h) | Long-lived token for session renewal |
| Secret Key | `CLAIMIQ_JWT_SECRET` | *Dev fallback* | In production, must be explicitly configured |

---

## 3. Role-Based Access Control (RBAC)

The Phase 7 API enforces 4 canonical roles:

| Role | Scope | Permitted Access |
|---|---|---|
| `ADMIN` | System Operations | Full read access across all claims, QA runs, analytics, and entity directories |
| `ANALYST` | Operations & Insights | Access to claims, analytics, scorecards, trends, payers, and providers |
| `QA_REVIEWER` | Quality Assurance | Access to QA rules, execution runs, detection telemetry, issues, and score breakdowns |
| `VIEWER` | Read-Only Observer | Basic read access to directory summaries and health diagnostics |

---

## 4. Password Security

- Passwords are never stored or logged in plaintext.
- Password hashing uses **PBKDF2-HMAC-SHA256** with:
  - 100,000 iterations
  - Cryptographically secure 16-byte random salt per user
  - Format: `pbkdf2_sha256$<iterations>$<salt>$<hex_digest>`
  - Constant-time hash verification via `secrets.compare_digest` to prevent timing attacks.

---

## 5. In-Memory User Store (Phase 7 Scope)

Per the canonical roadmap, the relational database does not contain a `users` table prior to dedicated IAM phases. Phase 7 maintains a thread-safe, in-memory user registry pre-seeded for development and testing:

```python
{
    "admin": {"role": "ADMIN", ...},
    "analyst": {"role": "ANALYST", ...},
    "qa_reviewer": {"role": "QA_REVIEWER", ...},
    "viewer": {"role": "VIEWER", ...},
}
```

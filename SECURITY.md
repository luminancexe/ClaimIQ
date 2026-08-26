# Security Policy

## Supported Versions

ClaimIQ is an active developmental healthcare claims data operations platform.

| Version / Phase | Supported |
| :--- | :---: |
| Phase 7 (v0.7.x) | :white_check_mark: |
| Phase 1–6 | :white_check_mark: |

---

## Reporting a Vulnerability

If you discover a potential security issue within ClaimIQ (such as unintended secret exposure, authentication flaws, or data leakage vulnerabilities):

1. **Do not** open a public issue on GitHub.
2. Please report the issue privately by contacting the project maintainers directly.
3. Include detailed reproduction steps, environment details, and affected components.

---

## Secret & Credential Handling Policy

1. **Synthetic Data Exclusivity**: ClaimIQ operates exclusively on deterministic synthetic healthcare data. No real Protected Health Information (PHI) or production payer credentials should ever be stored or transmitted.
2. **Zero Plaintext Secrets**: All environment-specific passwords and JWT signing keys must be supplied via environment variables (`CLAIMIQ_DB_PASSWORD`, `CLAIMIQ_JWT_SECRET`) or local `.env` files.
3. **Strict Ignore Rules**: All `.env`, `.env.*`, `*.pem`, `*.key`, `*.pfx`, and credential files are strictly excluded from source control via `.gitignore`.
4. **Read-Only Database Safeguards**: The API and analytical service layers execute under `SET SESSION TRANSACTION READ ONLY` to prevent accidental operational data mutation.

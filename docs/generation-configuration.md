# ClaimIQ — Generation Configuration & Scale Profiles

## 1. Official Scale Profiles

The ClaimIQ generator supports three predefined target scale profiles:

| Profile Target | Small (Dev/Test) | Medium (QA Staging) | Large (Benchmark Scale) |
| :--- | :---: | :---: | :---: |
| **Patients** | 100 | 1,000 | 10,000 |
| **Facilities** | 10 | 25 | 100 |
| **Providers** | 20 | 100 | 500 |
| **Payers** | 5 | 10 | 20 |
| **Insurance Plans** | 10 | 20 | 40 |
| **Encounters** | 500 | 5,000 | 50,000 |
| **Claims** | **1,000** | **10,000** | **100,000** |
| **Estimated Claim Lines** | ~2,500 | ~25,000 | ~250,000 |
| **Estimated Payments** | ~850 | ~8,500 | ~85,000 |

---

## 2. Configuration Parameters & Environment Variables

| CLI Parameter | Environment Variable | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `--scale` | `CLAIMIQ_SCALE` | `small` | Target sizing profile (`small`, `medium`, `large`). |
| `--seed` | `CLAIMIQ_SEED` | `42` | Deterministic pseudo-random seed integer. |
| `--batch-size` | `CLAIMIQ_BATCH_SIZE`| `2500` | Number of parameterized records per `executemany` chunk. |
| `--db-host` | `CLAIMIQ_DB_HOST` / `MYSQL_HOST` | `127.0.0.1` | MySQL server hostname or IP address. |
| `--db-port` | `CLAIMIQ_DB_PORT` / `MYSQL_PORT` | `3306` | MySQL server port. |
| `--db-name` | `CLAIMIQ_DB_NAME` / `MYSQL_DATABASE` | `claimiq_test` | Target database schema name. |
| `--db-user` | `CLAIMIQ_DB_USER` / `MYSQL_USER` | `root` | Database authentication username. |
| `--db-password` | `CLAIMIQ_DB_PASSWORD` / `MYSQL_PASSWORD`| `""` | Database authentication password. |
| `--dry-run` | — | `False` | Simulates in-memory generation without database insertion. |
| `--validate` | — | `False` | Runs the SQL data quality validation suite against existing database. |
| `--reset` | — | `False` | Safely purges transactional/master data in dependency-safe order. |

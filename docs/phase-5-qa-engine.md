# ClaimIQ — Phase 5 Data Quality & QA Rule Engine

## 1. Executive Summary & Engine Purpose

Phase 5 delivers the **Data Quality & QA Rule Engine** for ClaimIQ. The QA engine is designed to execute deterministic, database-backed SQL validation rules against ClaimIQ's MySQL 8.x claims datasets, detect anomalies introduced during Phase 4 error injection, persist execution telemetry and defect records (`qa_execution_runs`, `qa_results`, and `issues`), and empirically measure detection accuracy against ground truth (`anomaly_ground_truth`).

```mermaid
graph TD
    CLI[QA CLI: python -m qa] --> ENGINE[QA Execution Engine]
    ENGINE --> REG[Rule Registry (R-E001 to R-E067)]
    
    subgraph "QA Rule Suite (7 DQ Dimensions)"
        REG --> R1[Completeness: R-E001 to R-E010]
        REG --> R2[Uniqueness: R-E011 to R-E015]
        REG --> R3[Referential Integrity: R-E016 to R-E022]
        REG --> R4[Financial: R-E023 to R-E033]
        REG --> R5[Temporal: R-E034 to R-E042]
        REG --> R6[Accuracy: R-E043 to R-E060]
        REG --> R7[Validity: R-E061 to R-E067]
    end
    
    ENGINE --> LIVE_DB[(MySQL 8.x Database)]
    ENGINE --> LOG_RUNS[(qa_execution_runs)]
    ENGINE --> LOG_RES[(qa_results)]
    ENGINE --> LOG_ISS[(issues)]
    
    ENGINE --> SCORE[7-Dimension DQ Scoring Engine]
    ENGINE --> EVAL[Ground Truth Evaluator]
    EVAL --> GT[(anomaly_ground_truth)]
    EVAL --> METRICS[True Positives, Precision, Recall, F1]
```

---

## 2. Architecture & Directory Structure

The QA engine is organized within the `qa/` package:

| Module | File Path | Purpose |
| :--- | :--- | :--- |
| **CLI Runner** | [`qa/cli.py`](file:///D:/Projects/ClaimIQ/qa/cli.py) | CLI interface for `--run`, `--rule`, `--category`, `--dimension`, `--dry-run`, `--validate-ground-truth`, `--validate-clean`, `--report`, and `--list-rules`. |
| **Main Entrypoint** | [`qa/__main__.py`](file:///D:/Projects/ClaimIQ/qa/__main__.py) | Direct entry point for `python -m qa`. |
| **Config** | [`qa/config.py`](file:///D:/Projects/ClaimIQ/qa/config.py) | Configuration for batch identifiers, run references, dry-run flags, and database connectivity. |
| **Core Models** | [`qa/models.py`](file:///D:/Projects/ClaimIQ/qa/models.py) | Dataclasses for `QARuleDefinition`, `QADetectionRecord`, `QARunTelemetry`, `DQDimensionScore`, `DQScoreSummary`, and `GroundTruthEvaluationResult`. |
| **Rule Registry** | [`qa/registry.py`](file:///D:/Projects/ClaimIQ/qa/registry.py) | Authoritative registry of all 67 QA rules mapped to `E001`–`E067` and the 7 DQ dimensions. |
| **Database Persistence** | [`qa/database.py`](file:///D:/Projects/ClaimIQ/qa/database.py) | Synchronization of `qa_rules`, logging to `qa_execution_runs`, batch insertion into `qa_results`, and `issues` persistence. |
| **7-Dimension Scoring** | [`qa/scoring.py`](file:///D:/Projects/ClaimIQ/qa/scoring.py) | Deterministic calculation of dimensional scores and weighted overall DQ score. |
| **Ground Truth Evaluator**| [`qa/ground_truth.py`](file:///D:/Projects/ClaimIQ/qa/ground_truth.py) | Empirical matching against `anomaly_ground_truth` and calculation of True Positives, False Positives, False Negatives, Precision, Recall, and F1 score. |
| **Validators** | [`qa/validators.py`](file:///D:/Projects/ClaimIQ/qa/validators.py) | Clean baseline verification and rule registry integrity auditing. |
| **Execution Engine** | [`qa/engine.py`](file:///D:/Projects/ClaimIQ/qa/engine.py) | Orchestrator executing rules, capturing execution latencies, recording telemetry, and producing execution summaries. |
| **Rule Modules** | [`qa/rules/`](file:///D:/Projects/ClaimIQ/qa/rules/) | 8 category-specific rule modules containing individual SQL detection logic. |

---

## 3. Command-Line Interface Usage

```bash
# 1. List all 67 registered QA rules with categories, dimensions, and severities
python -m qa --list-rules

# 2. Execute dry-run simulation across all rules
python -m qa --dry-run

# 3. Execute dry-run for a specific category (e.g. FINANCIAL)
python -m qa --dry-run --category FINANCIAL

# 4. Execute QA rule engine against database with custom batch ID
python -m qa --run --batch-id BATCH-2026-001

# 5. Execute QA rule engine with Ground Truth validation and detailed report
python -m qa --run --validate-ground-truth --report

# 6. Audit clean baseline integrity (verifies zero unexpected defects)
python -m qa --validate-clean
```

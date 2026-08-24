# ClaimIQ — QA Execution Engine & Telemetry Logging

## 1. Execution Workflow

The QA Engine execution cycle operates in an ACID-compliant, auditable pipeline:

```mermaid
sequenceDiagram
    participant CLI as QA CLI (python -m qa)
    participant ENG as QAExecutionEngine
    participant REG as QA Rule Registry
    participant DB as MySQL Database
    participant SCORE as Scoring Engine
    participant GT as Ground Truth Evaluator

    CLI->>ENG: execute()
    ENG->>REG: get_effective_rules()
    ENG->>DB: sync_qa_rules_to_database()
    
    loop For Each QA Rule
        ENG->>DB: Execute Rule SQL / Validator
        DB-->>ENG: Telemetry (records, defects, latency) + Detections
    end

    ENG->>SCORE: calculate_dq_score()
    SCORE-->>ENG: 7-Dimension DQScoreSummary
    
    ENG->>GT: evaluate_ground_truth_accuracy()
    GT-->>ENG: GroundTruthEvaluationResult (TP, FP, FN, Precision, Recall, F1)
    
    opt If Not Dry Run
        ENG->>DB: record_qa_execution_run()
        ENG->>DB: save_qa_results()
        ENG->>DB: save_detected_issues()
    end

    ENG-->>CLI: Comprehensive Execution Summary
```

---

## 2. Telemetry and Run Persistence Schema

### 1. `qa_execution_runs` Table
Captures batch-level execution metadata, start/end timestamps, total records evaluated, total defects detected, and the aggregate DQ score.

### 2. `qa_results` Table
Captures granular per-rule metrics including execution duration in milliseconds, records scanned, defect count, and execution status (`SUCCESS` / `SKIPPED`).

### 3. `issues` Table
Persists detected defect instances with severity codes, dimension codes, variance amounts, and initial status `Detected` for operational tracking.

# ClaimIQ — Project Overview

## 1. Executive Summary

**ClaimIQ** is a synthetic-data healthcare claims data quality and operations platform designed to enable Data Operations Analysts, Quality Analysts, and Revenue Cycle Management (RCM) teams to systematically analyze claims, detect data quality anomalies, investigate financial discrepancies, monitor operational KPIs, and maintain rigorous, auditable QA workflows.

In modern healthcare revenue cycles, data discrepancies between providers, billing systems, clearinghouses, and payers result in millions of dollars in administrative waste, delayed reimbursements, and erroneous claim denials. ClaimIQ provides an end-to-end operational framework to monitor, validate, triage, and resolve data integrity issues within a simulated, highly realistic healthcare claims environment.

> [!IMPORTANT]
> **Synthetic Data Mandate**: ClaimIQ operates strictly on synthetic healthcare data. It never connects to, ingests, or stores real Protected Health Information (PHI), medical records, or genuine member/payer information.

---

## 2. Problem Statement

Healthcare claims data pipelines suffer from frequent data quality and reconciliation breakdowns, including:
- **Upstream Data Ingestion Failures**: Missing patient identifiers, invalid National Provider Identifiers (NPI), malformed taxonomy codes, and duplicate billings.
- **Financial & Adjudication Mismatches**: Billed amounts diverging from the sum of payments, contractual adjustments, and patient responsibilities, leading to unverified write-offs or undetected overpayments.
- **Temporal & Workflow Discrepancies**: Impossible date sequences (e.g., payment or adjudication occurring prior to service delivery or submission).
- **Referential Integrity Loss**: Orphaned claim lines, unmapped transaction references, and dangling provider records across disparate billing feeds.
- **Operational Blindspots**: Lack of standardized issue tracking, root-cause documentation, and resolution lifecycle metrics for RCM operations teams.

ClaimIQ resolves these operational challenges by providing automated rule-based validation, centralized issue investigation workbenches, operational reporting, and auditable root-cause documentation.

---

## 3. Who Uses ClaimIQ

ClaimIQ is built specifically for data and operational roles within healthcare organizations, Management Services Organizations (MSOs), healthcare analytics vendors, and RCM service providers:

1. **Data Operations Analysts**: Conduct daily batch validation, investigate referential and financial discrepancies, track root causes, and correct operational data pipelines.
2. **QA / Data Quality Analysts**: Design, test, and tune data quality validation rules, ensure data completeness and consistency across synthetic data pipelines.
3. **Operations Managers**: Track team resolution velocity, monitor SLA adherence, evaluate provider/payer error rates, and analyze trends in recurring claim defects.
4. **System Administrators**: Manage data pipelines, execute validation batches, configure system settings, and enforce role-based access.
5. **Read-Only / Reporting Users / Auditors**: Review data quality scorecards, compliance logs, and operational audit trails.

---

## 4. Why ClaimIQ is Useful

- **Proactive Anomaly Detection**: Catches billing anomalies, schema violations, and business logic flaws before downstream financial reconciliation or reporting is compromised.
- **Auditable Issue Lifecycle**: Transitions issues through a structured state machine (`Detected` $\rightarrow$ `Open` $\rightarrow$ `Investigating` $\rightarrow$ `Resolved` / `Escalated` / `False Positive`), ensuring end-to-end traceability.
- **Operational & Financial Transparency**: Provides real-time visibility into claim health scores, financial leakage risks, and payer adjudication variances.
- **Root-Cause Knowledge Base**: Maintains standardized documentation and investigation notes to prevent repeated operational errors.

---

## 5. System Identity & Distinct Boundaries

To avoid architectural and functional ambiguity, ClaimIQ has clearly defined boundaries. The table below delineates what ClaimIQ is versus what it is explicitly **not**:

| Feature / Domain | ClaimIQ Platform | What ClaimIQ is NOT |
| :--- | :--- | :--- |
| **Primary Focus** | Data Quality, Integrity, & Operational RCM Anomaly Detection | Electronic Health Record (EHR) or Practice Management System |
| **Clinical Decisioning** | **None**. Claims are analyzed purely for operational & financial integrity | Medical diagnosis, clinical triage, or patient treatment planning |
| **Claims Adjudication** | Simulates and verifies the consistency of adjudication outcomes | A live payer clearinghouse or adjudication engine |
| **Financial Processing** | Audits payment balances and adjustments for mathematical correctness | A payment gateway, bank merchant account, or electronic fund transfer system |
| **Data Environment** | **100% Synthetic Healthcare Data** | Production system handling HIPAA-regulated Protected Health Information (PHI) |

```mermaid
graph TD
    subgraph "Excluded Domains"
        EHR[Electronic Health Records]
        CDSS[Clinical Decision Support]
        LIVE_PAYER[Live Payer Clearinghouse]
        BANK[Live Banking / EFT]
    end

    subgraph "ClaimIQ Platform Scope"
        INGEST[Synthetic Data Ingestion] --> VAL[Data Quality & SQL QA Engine]
        VAL --> ANOMALY[Anomaly Detection & Triage]
        ANOMALY --> WORKBENCH[Operations Investigation Workbench]
        WORKBENCH --> REPORT[Operational & Metric Reporting]
        WORKBENCH --> AUDIT[Traceability & Audit Logs]
    end

    EHR -.->|Out of Scope| ClaimIQ Platform Scope
    LIVE_PAYER -.->|Out of Scope| ClaimIQ Platform Scope
```

---

## 6. Portfolio & Professional Alignment

ClaimIQ is engineered to demonstrate high-competency data operations capabilities:
- **Advanced SQL & Relational Modeling**: Complex joins, window functions, and integrity constraints for automated QA rule engines.
- **Data Quality & Integrity Assurance**: Comprehensive rules across 7 core data quality dimensions.
- **Healthcare RCM Proficiency**: In-depth understanding of standard claims structures (837/835 equivalents, claim lines, CPT/HCPCS, ICD-10, NPI, CARC/RARC adjustments).
- **Root-Cause Analysis & SOP Documentation**: Structured operational investigation workflows, issue classification, and resolution standard operating procedures.
- **Operational Reporting**: Actionable metric frameworks, data quality scorecards, and executive summaries.

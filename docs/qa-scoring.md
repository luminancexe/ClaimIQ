# ClaimIQ — Data Quality Scoring Methodology

## 1. 7-Dimension Governance Model

Data Quality scores in ClaimIQ are calculated across seven foundational dimensions defined in `ref_dq_dimensions`:

| Dimension Code | Dimension Name | Statutory Weight | Description |
| :--- | :--- | :---: | :--- |
| **Referential Integrity** | Referential Integrity | **0.20** | Entity relationship consistency and foreign key validity. |
| **Financial** | Financial Integrity | **0.20** | Mathematical accuracy of billing, payments, write-offs, and balances. |
| **Completeness** | Completeness | **0.15** | Presence of mandatory demographics, descriptions, and line items. |
| **Validity** | Validity & Conformance | **0.15** | Format conformance for NPI (Luhn), CPT, ICD-10, and TINs. |
| **Uniqueness** | Uniqueness | **0.10** | Absence of duplicate claims, service lines, and payments. |
| **Temporal** | Temporal Consistency | **0.10** | Chronological ordering of clinical encounters, submissions, and payments. |
| **Accuracy** | Accuracy & State Logic | **0.10** | Claim lifecycle state consistency and business logic conformance. |
| **Total** | — | **1.00** (100%) | — |

---

## 2. Scoring Formula & Severity Penalty Weights

For each dimension $d$, the raw score $S_d \in [0.0, 100.0]$ is computed based on severity-weighted defect penalties relative to evaluated population $N_d$:

$$P_d = \sum_{i \in \text{Defects}_d} \text{Penalty}(\text{Severity}_i)$$

Where severity penalty multipliers are:
- **Critical Severity**: $3.0$
- **High Severity**: $2.0$
- **Medium Severity**: $1.0$
- **Low Severity**: $0.5$

The raw dimensional score is calculated as:

$$S_d = \max\left(0.0, 100.0 - \left(\frac{P_d}{\max(N_d, 1)} \times 100 \times 5.0\right)\right)$$

The aggregate weighted Data Quality Score is:

$$\text{Overall DQ Score} = \sum_{d=1}^{7} \left(S_d \times \text{Weight}_d\right)$$

- **Clean Baseline Property**: When $\text{Defects}_d = 0$ across all dimensions, $S_d = 100.00$ and $\text{Overall DQ Score} = 100.00$.

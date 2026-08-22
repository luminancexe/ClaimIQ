# ClaimIQ — Synthetic Data Model & Domain Rules

## 1. Domain Entities & Referential Dependencies

ClaimIQ synthesizes a realistic healthcare claims ecosystem across 17 interconnected entity tables:

```text
facilities (Independent)
    ↓
providers (Linked to facilities with Luhn NPIs)

payers (Independent)
    ↓
insurance_plans (Linked to payers)

patients (Independent demographics, age 18-85)
    ↓
patient_coverage (Links patients to insurance_plans)

encounters (Links patients, providers, facilities)
    ↓
encounter_diagnoses (Itemized ICD-10 diagnostic codes)
    ↓
claims (Billing claim header linking encounters, patients, providers, payers)
    ↓
claim_lines (Itemized CPT procedure service lines)
    ↓
claim_status_history (Audit log of claim state transitions)
    ↓
remittances (ERA 835 batch headers linking payers)
    ↓
payments (Disbursed cash allocations linking remittances to claims)
    ↓
adjustments (Contractual CO and patient responsibility PR write-offs)
    ↓
denials (Itemized CARC determinations)
    ↓
reconciliations (Mathematical balancing ledger)
```

---

## 2. Mathematical Invariants & Clean Baseline Rules

In Phase 3, every generated synthetic transaction preserves strict mathematical equalities:

### 1. Claim Itemization Equality
$$\text{claims.total\_billed\_amount} = \sum_{i=1}^{N} \text{claim\_lines.line\_billed\_amount}_i$$
$$\text{claim\_lines.line\_billed\_amount} = \text{units} \times \text{unit\_price}$$

### 2. Remittance Batch Equality
$$\text{remittances.total\_paid\_amount} = \sum \text{payments.paid\_amount (for that remittance\_id)}$$

### 3. Financial Reconciliation Balancing
For all adjudicated claims in the clean baseline dataset:
$$\text{total\_billed} = \text{total\_paid} + \text{total\_adjusted} + \text{total\_patient\_resp}$$
$$\text{variance\_amount} = \text{total\_billed} - (\text{total\_paid} + \text{total\_adjusted} + \text{total\_patient\_resp}) = \$0.00$$
$$\text{reconciliation\_status} = \text{'BALANCED'}$$

---

## 3. Claim Lifecycle & Status Transitions

### Current Status Distributions (Clean Baseline)
- **`Paid`** (75%): Adjudicated in full. Contains payment transaction and zero-variance reconciliation.
- **`Partially Paid`** (15%): Adjudicated with partial cash reimbursement, contractual adjustment (`CO-45`), and patient copayment (`PR-1`).
- **`Denied`** (7%): Adjudicated with formal refusal (`CO-16`, `PR-204`), zero cash payment, and balancing contractual write-off.
- **`Active / In-Flight`** (3%): Subdivided deterministically between `Submitted` (1%), `Accepted` (1%), and `Pending` (1%). Zero finalized payments or adjudications.

### State Transition FSM Paths
1. `Submitted` $\rightarrow$ `Accepted` $\rightarrow$ `Paid`
2. `Submitted` $\rightarrow$ `Accepted` $\rightarrow$ `Partially Paid`
3. `Submitted` $\rightarrow$ `Accepted` $\rightarrow$ `Denied`
4. `Submitted` $\rightarrow$ `Accepted` $\rightarrow$ `Pending`
5. `Submitted` (Active in-flight)

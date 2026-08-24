# Provider & Payer Scorecards

## Overview
Phase 6 produces entity-level scorecards for healthcare providers and insurance payers, applying safe SQL aggregation to eliminate one-to-many Cartesian multiplication.

## Provider Quality Scorecards
Provider attribution is derived from `claims.billing_provider_id` mapped to `providers` and `facilities`.

### Scorecard Metrics:
- **Provider Reference & Name**: Unique identifier (e.g. `PRV-2026-0000001`) and full name.
- **Specialty & Facility**: Primary taxonomy specialty and affiliated facility name.
- **Claim Volume**: Total count of submitted claims.
- **Total Billed & Paid**: Fixed-point monetary aggregates.
- **Payment Conversion Rate**: $\frac{\text{Total Paid}}{\text{Total Billed}} \times 100\%$.
- **Denial Rate**: $\frac{\text{Denied Claims}}{\text{Total Claims}} \times 100\%$.
- **Issue Count & Defect Density**: $\frac{\text{Attributed Issues}}{\text{Claim Volume}}$.
- **Data Quality Score**: $\max(0.0, 100.0 - (\text{Issue Density} \times 100 \times 2.0))$.
- **Financial Exposure**: Total variance and overpayment at risk linked to the provider's claims.

## Payer Adjudication Scorecards
Payer attribution is derived from `claims.payer_id` mapped to `payers`.

### Scorecard Metrics:
- **Payer Reference & Name**: Unique identifier (e.g. `PAY-2026-0000001`) and entity title.
- **Payer Type**: Commercial, Medicare, Medicaid, Self-Pay, etc.
- **Claim Volume**: Total claims submitted to this payer.
- **Total Billed & Paid**: Total billed charges and total paid reimbursements.
- **Denial Rate**: Percentage of claims denied by the payer.
- **Payment Rate**: Percentage of billed charges collected.
- **Adjudication Latency**: Average turnaround days from `submission_date` to `adjudication_date`.
- **Payment Latency**: Average turnaround days from `submission_date` to `payment_date`.
- **Timely Filing Compliance**: Percentage of claims submitted within payer-defined `timely_filing_days`.
- **Contractual Write-Off Ratio**: $\frac{\text{Total CO Adjustments}}{\text{Total Billed}} \times 100\%$.
- **Issue Count**: QA defects attributed to claims processed by this payer.

## Deterministic Ordering
Scorecards are sorted deterministically:
1. Provider: `ORDER BY claim_volume DESC, total_billed DESC, provider_id ASC`
2. Payer: `ORDER BY claim_volume DESC, total_billed DESC, payer_id ASC`

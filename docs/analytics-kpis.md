# Operational & Quality Assurance KPIs

## Overview
Phase 6 aggregates multi-domain operational KPIs spanning claims intake, payment disbursements, adjudication denials, and data quality issue detections.

## Metric Catalog

### 1. Claims Operational KPIs
- **Total Volume**: Total count of claims in the dataset.
- **Status Distribution**: Frequency and percentage across `Submitted`, `Accepted`, `Paid`, `Partially Paid`, `Denied`, `Pending`, `Rejected`.
- **Adjudicated Volume**: Count of claims with non-null `adjudication_date`.
- **Adjudication Rate**: $\frac{\text{Adjudicated Claims}}{\text{Total Claims}} \times 100\%$.
- **Reconciled Volume**: Count of claims with `is_reconciled = 1`.

### 2. Payment KPIs
- **Total Disbursements**: Total count of rows in `payments`.
- **Total Paid Amount**: $\sum \text{payments.paid\_amount}$.
- **Average Payment Amount**: $\frac{\text{Total Paid}}{\text{Total Disbursements}}$.
- **Zero Payment Count**: Count of payment transactions with `paid_amount = 0.00`.
- **Average Turnaround**: $\text{AVG}(\text{payment\_date} - \text{submission\_date})$ in calendar days.

### 3. Denial KPIs
- **Total Denials**: Total count of rows in `denials`.
- **Denial Rate**: $\frac{\text{Total Denials}}{\text{Adjudicated Claims}} \times 100\%$.
- **Appealable Rate**: $\frac{\text{Appealable Denials}}{\text{Total Denials}} \times 100\%$.
- **Top Denial Reasons**: Top 5 CARC codes and descriptions ranked by occurrence.
- **Denial Financial Exposure**: $\sum \text{claims.total\_billed\_amount WHERE current\_status\_code} = \text{'Denied'}$.

### 4. Quality Assurance KPIs
- **Total Issues**: Total count of records in `issues`.
- **Severity Breakdown**: Counts categorized into `Critical`, `High`, `Medium`, `Low`.
- **Dimension Breakdown**: Counts across the 7 governance dimensions.
- **Average DQ Score**: Mean DQ score across historical execution runs.
- **Clean Record Rate**: $\left(\frac{\text{Total Claims} - \text{Defective Claims}}{\text{Total Claims}}\right) \times 100\%$.
- **Defect Density**: $\frac{\text{Total Issues Detected}}{\text{Total Claims Evaluated}}$.

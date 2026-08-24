# Financial Exposure & Reconciliation Analytics

## Governing Financial Invariant
ClaimIQ enforces the fundamental healthcare reimbursement invariant:
$$\text{Total Billed} = \text{Total Paid} + \text{Total Contractual Adjustments} + \text{Total Patient Responsibility} + \text{Variance}$$

On clean datasets:
$$\text{Variance} = \$0.00, \quad \text{Financial Integrity Rate} = 100.00\%$$

## Mathematical Definitions & Metrics

### 1. Total Billed Amount
$$\text{Total Billed} = \sum \text{claims.total\_billed\_amount}$$

### 2. Total Paid Amount
$$\text{Total Paid} = \sum \text{payments.paid\_amount}$$

### 3. Total Contractual Adjustments (CO)
$$\text{Total Contractual} = \sum \text{adjustments.adjustment\_amount} \quad (\text{WHERE } \text{group\_code} = \text{'CO'})$$

### 4. Total Patient Responsibility (PR)
$$\text{Total Patient Resp} = \sum \text{reconciliations.total\_patient\_resp}$$

### 5. Reconciliation Variance
$$\text{Total Variance} = \sum \text{reconciliations.variance\_amount}$$

### 6. Overpayment Exposure
$$\text{Overpayment Exposure} = \sum \max(0, \text{paid\_amount} - \text{billed\_amount})$$

### 7. Underpayment / Discrepancy Exposure
$$\text{Underpayment Exposure} = \sum |\text{reconciliations.variance\_amount}| \quad (\text{WHERE } \text{variance\_amount} \ne 0.00)$$

### 8. Reconciliation Rate
$$\text{Reconciliation Rate} = \left(\frac{\text{Count}(\text{claims WHERE is\_reconciled} = 1)}{\text{Count}(\text{claims WHERE status IN ('Paid', 'Partially Paid', 'Denied')})}\right) \times 100\%$$

### 9. Payment Rate (Conversion)
$$\text{Payment Rate} = \left(\frac{\text{Total Paid}}{\text{Total Billed}}\right) \times 100\%$$

### 10. Financial Integrity Rate
$$\text{Financial Integrity Rate} = \max\left(0.00, 100.00 - \left(\frac{\sum |\text{variance\_amount}|}{\max(\text{Total Billed}, 1)} \times 100\right)\right)$$

All monetary values are calculated using fixed-point `Decimal` (quantized to `0.01`, `ROUND_HALF_UP`) with zero floating-point representation.

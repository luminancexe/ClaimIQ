# Recurrence & Repeat Offender Analytics

## Overview
Phase 6 detects systematic, repeated defect patterns across billing entities, identifying providers, payers, or rules exhibiting clustered non-compliance.

## Recurrence Threshold & Clustering Rules
- **Cluster Criterion**: A combination of `(entity_type, entity_identifier, rule_code)` must occur **$\ge 2$ times** to qualify as a recurring defect cluster.
- **Repeat Rate**:
  $$\text{Repeat Issue Rate} = \left(\frac{\sum_{\text{clusters}} \text{Occurrences}}{\text{Total Issues}}\right) \times 100\%$$

## Entity Types Analyzed
1. `PROVIDER`: Repeat violations originating from the same billing physician or group.
2. `PAYER`: Systematic adjudication or payment anomalies linked to a single insurance carrier.
3. `RULE`: Universal rule violations repeated across claims.

## Deterministic Ordering
Clustered patterns are sorted deterministically:
$$\text{ORDER BY occurrence\_count DESC, entity\_type ASC, entity\_identifier ASC, rule\_code ASC}$$

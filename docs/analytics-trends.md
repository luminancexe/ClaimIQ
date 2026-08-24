# Longitudinal Data Quality Trends

## Overview
Phase 6 provides chronological time-series aggregations of data quality health and volume trajectories across configurable time intervals.

## Supported Time Buckets
- **Daily**: `%Y-%m-%d` (e.g. `2026-01-15`)
- **Weekly**: `%Y-W%u` (e.g. `2026-W03`)
- **Monthly**: `%Y-%m` (e.g. `2026-01`)

## Trend Metrics & Trajectory Logic

### 1. Longitudinal Data Point (`DQTrendPoint`)
- `time_bucket`: ISO time interval identifier.
- `claim_volume`: Total claim intake during the bucket window.
- `issue_count`: Total QA defects detected on claims within the bucket window.
- `dimension_scores`: 7-dimension breakdown for that time window.
- `overall_dq_score`: Weighted multi-dimension quality score.

### 2. Trend Velocity & Direction Classification
Score velocity measures the linear rate of change across the series:
$$\text{Score Velocity} = \frac{\text{Score}_{\text{last}} - \text{Score}_{\text{first}}}{\max(N - 1, 1)}$$

**Trajectory Classification Rules**:
- $\text{Score Velocity} \ge +0.50 \implies \mathbf{IMPROVING}$
- $\text{Score Velocity} \le -0.50 \implies \mathbf{DEGRADING}$
- $-0.50 < \text{Score Velocity} < +0.50 \implies \mathbf{STABLE}$

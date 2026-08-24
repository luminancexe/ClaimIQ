# Root Cause & Pareto Defect Analysis

## Overview
Phase 6 applies the classic **Pareto Principle (80/20 Rule)** to identify the vital few defect categories and anomaly codes driving 80% of all data quality issues in the healthcare claims dataset.

## Mathematical Formulation

### 1. Defect Contribution
$$\text{Percentage Contribution}_i = \left(\frac{\text{Issue Count}_i}{\text{Total Issues Analyzed}}\right) \times 100\%$$

### 2. Cumulative Percentage
$$\text{Cumulative Percentage}_k = \sum_{i=1}^{k} \text{Percentage Contribution}_i$$

### 3. Pareto Cutoff Index
The index $k^*$ such that:
$$k^* = \min \{ k \mid \text{Cumulative Percentage}_k \ge 80.00\% \}$$

All anomaly codes with index $\le k^*$ are flagged as **vital drivers** (`[*]`).

### 4. Deterministic Ranking
Items are ranked deterministically:
$$\text{ORDER BY issue\_count DESC, financial\_exposure DESC, rule\_code ASC}$$

## Clean Dataset Boundary
On a clean dataset ($\text{Total Issues} = 0$), the engine returns an empty items catalog, cutoff index $0$, and reports `"None (Clean Dataset - Zero Defect Findings)"` without division errors.

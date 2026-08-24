# ClaimIQ — Ground Truth Accuracy Evaluation & Benchmarking

## 1. Evaluation Methodology

Phase 5 evaluates QA detection accuracy by matching live detected defects against the Phase 4 `anomaly_ground_truth` registry.

Ground truth comparison uses a deterministic compound identifier:

$$\text{Match Key} = \text{anomaly\_code} + \text{"|"} + \text{target\_table} + \text{"|"} + \text{target\_record\_id}$$

---

## 2. Confusion Matrix & Accuracy Metrics

```mermaid
graph TD
    subgraph "Ground Truth vs Detections"
        TP[True Positives (TP)<br/>Injected Anomaly Correctly Detected]
        FP[False Positives (FP)<br/>Clean Record Erroneously Flagged]
        FN[False Negatives (FN)<br/>Injected Anomaly Missed by QA Rules]
    end

    TP & FP --> P["Precision = TP / (TP + FP)"]
    TP & FN --> R["Recall = TP / (TP + FN)"]
    P & R --> F1["F1 Score = 2 * (P * R) / (P + R)"]
```

### Metrics Definitions:
- **Precision**: Proportion of flagged anomalies that are verified ground truth defects:
  $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$
- **Recall (Detection Rate)**: Proportion of total injected ground truth defects that were successfully identified:
  $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
- **F1 Score**: Harmonic mean of Precision and Recall:
  $$\text{F1} = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## 3. Zero-Denominator Handling

- If both ground truth and detections are zero (e.g. clean dataset evaluation):
  $$\text{Precision} = 1.0000, \quad \text{Recall} = 1.0000, \quad \text{F1} = 1.0000$$
- If ground truth defects exist but zero detections are made:
  $$\text{Precision} = 0.0000, \quad \text{Recall} = 0.0000, \quad \text{F1} = 0.0000$$

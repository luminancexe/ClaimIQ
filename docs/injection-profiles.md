# ClaimIQ — Injection Profiles & Targeting Strategy

## 1. Profile Matrix & Defect Rates

The ClaimIQ Error Injection Engine defines five standardized profiles for generating controlled anomalous datasets:

| Profile Name | Target Defect Rate | Mutations per Code | Total Defects (All 67 Codes) | Target Use Case |
| :--- | :---: | :---: | :---: | :--- |
| **`clean`** | **0%** | **0** | **0** | Pure Phase 3 baseline validation; zero mutations. |
| **`light`** | **~1%** | **1** | **67** | High-precision baseline sensitivity testing & false-positive evaluation. |
| **`moderate`** | **~5%** | **3** | **201** | Standard QA testing baseline; balanced defect distribution across all categories. |
| **`heavy`** | **~10%** | **7** | **469** | Stress-testing QA rule engines, aggregations, and severity escalations. |
| **`targeted`** | **User-Configured** | **Custom** | **User-Defined** | Targeted rule verification (e.g. testing only overpayments or temporal breaks). |

---

## 2. Severity Distribution by Profile

Based on the 67 registered anomaly definitions in the taxonomy:
- **Critical Anomalies (8 codes)**: `E023`, `E027`, `E028`, `E029`, `E030`, `E042`, `E052`, `E057`.
- **High Severity Anomalies (32 codes)**: `E006`, `E011`, `E012`, `E013`, `E015`, `E017`, `E019`, `E020`, `E021`, `E022`, `E024`, `E025`, `E031`, `E032`, `E033`, `E034`, `E035`, `E036`, `E037`, `E039`, `E040`, `E041`, `E043`, `E044`, `E045`, `E046`, `E051`, `E054`, `E055`, `E056`, `E059`, `E061`.
- **Medium Severity Anomalies (15 codes)**: `E002`, `E005`, `E010`, `E014`, `E016`, `E018`, `E026`, `E038`, `E047`, `E048`, `E049`, `E053`, `E058`, `E062`, `E063`.
- **Low Severity Anomalies (12 codes)**: `E001`, `E003`, `E004`, `E007`, `E008`, `E009`, `E050`, `E060`, `E064`, `E065`, `E066`, `E067`.

| Severity Tier | Share of Taxonomy | Light Profile Count | Moderate Profile Count | Heavy Profile Count |
| :--- | :---: | :---: | :---: | :---: |
| **Critical** | **11.9%** (8 / 67) | 8 | 24 | 56 |
| **High** | **47.8%** (32 / 67) | 32 | 96 | 224 |
| **Medium** | **22.4%** (15 / 67) | 15 | 45 | 105 |
| **Low** | **17.9%** (12 / 67) | 12 | 36 | 84 |
| **Total** | **100%** (67 / 67) | **67** | **201** | **469** |

---

## 3. Targeting & Sampling Rules

1. **Deterministic Target Selection**:
   - Target records are selected from eligible clean baseline rows using `GeneratorRandomState(seed).sample()`.
   - The same `(seed, profile)` pair always selects the exact same records and applies identical mutations.
2. **Disjoint Multi-Targeting**:
   - Target selections avoid compounding multiple unrelated mutations on the same row unless explicitly required by the anomaly logic.
3. **Reversibility Journaling**:
   - Every mutation captures the pre-mutation value in `original_value` and the post-mutation value in `mutated_value` to enable two-way rollback via `--reset-anomalies`.

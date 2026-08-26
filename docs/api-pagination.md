# ClaimIQ REST API: Pagination & Filtering Model

## 1. Overview

All list endpoints in ClaimIQ Phase 7 implement a deterministic pagination model wrapped in a generic `PaginatedResponse[T]` schema. This guarantees predictable response envelopes and prevents unbounded database queries.

---

## 2. Request Parameters

| Parameter | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `page` | `integer` | `1` | `ge=1` | 1-based page index |
| `page_size` | `integer` | `50` | `ge=1, le=500` | Number of records to return per page |

Requests with `page < 1` or `page_size > 500` are rejected immediately with HTTP `422 Unprocessable Entity`.

---

## 3. Response Schema

```json
{
  "page": 1,
  "page_size": 50,
  "total": 1250,
  "total_pages": 25,
  "has_next": true,
  "has_previous": false,
  "items": [ ... ]
}
```

### Metadata Calculation Formulas:
- $\text{total\_pages} = \lceil \frac{\text{total}}{\text{page\_size}} \rceil$
- $\text{has\_next} = (\text{page} < \text{total\_pages})$
- $\text{has\_previous} = (\text{page} > 1 \land \text{total\_pages} > 0)$
- $\text{offset} = (\text{page} - 1) \times \text{page\_size}$

---

## 4. Endpoints Implementing Pagination

1. `/api/v1/claims`
2. `/api/v1/qa/runs`
3. `/api/v1/qa/issues`
4. `/api/v1/providers`
5. `/api/v1/payers`
6. `/api/v1/issues`

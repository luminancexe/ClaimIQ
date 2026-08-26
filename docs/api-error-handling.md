# ClaimIQ REST API: Error Handling & Security Guidelines

## 1. Overview

ClaimIQ Phase 7 enforces strict API error standardization to ensure client resilience while preventing any leakage of sensitive internal details (stack traces, SQL statements, database credentials, server paths, or secrets).

---

## 2. Standardized Error Response Envelope

Every error returned by the API follows the `ErrorResponse` schema:

```json
{
  "error_code": "NOT_FOUND",
  "message": "Claim with ID 9999 not found",
  "request_id": "req-c248935bf4e044da"
}
```

---

## 3. Standard HTTP Status Codes

| HTTP Status | Error Code | Description | Example Trigger |
|---|---|---|---|
| `400` | `BAD_REQUEST` | Malformed parameters or business logic error | Invalid trend interval parameter |
| `401` | `UNAUTHORIZED` | Missing, expired, or invalid JWT token | Protected endpoint called without Bearer header |
| `403` | `FORBIDDEN` | Insufficient role permissions | Viewer attempting administrative operations |
| `404` | `NOT_FOUND` | Requested entity does not exist | Nonexistent claim or provider ID |
| `422` | `VALIDATION_ERROR` | Schema or parameter validation failed | `page_size > 500` or non-integer ID in path |
| `500` | `INTERNAL_SERVER_ERROR` | Unhandled server exception | Database connectivity crash |

---

## 4. Security & Sanitization Guarantees

1. **SQL Suppression**: Raw SQL exception messages from PyMySQL or InnoDB are never passed to the HTTP response payload.
2. **Traceback Masking**: Unhandled exceptions return generic messages while logging details internally with the corresponding `request_id`.
3. **Request Tracing**: All error responses include the `request_id` (mirrored in the `X-Request-ID` response header) to enable audit tracing.

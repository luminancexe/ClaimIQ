"""Global Error Handling and Request ID Middleware for ClaimIQ Phase 7 Backend."""

import uuid
import re
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError


# Sanitizer for client-provided X-Request-ID (letters, digits, dashes, max 64 chars)
_SAFE_REQ_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Ensure every request has a validated or newly generated X-Request-ID."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        incoming_id = request.headers.get("X-Request-ID")
        if incoming_id and _SAFE_REQ_ID_RE.match(incoming_id):
            req_id = incoming_id
        else:
            req_id = f"req-{uuid.uuid4().hex[:16]}"

        # Store in request state for downstream handlers
        request.state.request_id = req_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response


def register_exception_handlers(app: FastAPI) -> None:
    """Register standardized JSON error handlers that prevent sensitive data leaks."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        req_id = getattr(request.state, "request_id", f"req-{uuid.uuid4().hex[:16]}")
        error_code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": error_code,
                "message": str(exc.detail),
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        req_id = getattr(request.state, "request_id", f"req-{uuid.uuid4().hex[:16]}")
        # Build clean user-facing error message from validation errors
        errors_summary = []
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err.get("loc", []))
            msg = err.get("msg", "Invalid value")
            errors_summary.append(f"{loc}: {msg}")
        joined_msg = "; ".join(errors_summary) if errors_summary else "Request validation failed"

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": joined_msg,
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = getattr(request.state, "request_id", f"req-{uuid.uuid4().hex[:16]}")
        # Generic handler NEVER returns stack traces, raw SQL, or internal paths
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred. Please contact support.",
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

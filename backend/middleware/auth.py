"""Authentication middleware and JWT helpers for ClaimIQ Phase 7 Backend."""

from fastapi import Request
from typing import Optional


def get_token_from_header(request: Request) -> Optional[str]:
    """Extract Bearer token string from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

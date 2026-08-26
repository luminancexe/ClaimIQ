"""Pydantic v2 schemas for authentication endpoints."""

from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """POST /api/v1/auth/login request body."""
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    """JWT token response after successful authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    """POST /api/v1/auth/refresh request body."""
    refresh_token: str


class UserProfile(BaseModel):
    """Authenticated user profile returned by GET /api/v1/auth/me."""
    user_id: str
    username: str
    role: str
    created_at: Optional[str] = None

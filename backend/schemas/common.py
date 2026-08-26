"""Pydantic v2 schemas shared across all ClaimIQ API endpoints."""

from typing import TypeVar, Generic, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Consistent paginated response envelope."""
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=500)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool
    items: List[T]


class ErrorResponse(BaseModel):
    """Standardized API error response."""
    error_code: str
    message: str
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database_connected: bool
    timestamp: str

"""Pydantic v2 schemas for issues endpoints."""

from typing import Optional
from pydantic import BaseModel


class IssueSummary(BaseModel):
    """Issue list item (paginated results)."""
    issue_id: int
    issue_reference: str
    rule_id: int
    claim_id: Optional[int] = None
    dimension_code: str
    severity_code: str
    current_status_code: str
    detected_at: str
    resolved_at: Optional[str] = None
    variance_amount: Optional[str] = None  # Decimal as string


class IssueDetail(BaseModel):
    """Full issue detail with rule metadata."""
    issue_id: int
    issue_reference: str
    rule_id: int
    rule_code: Optional[str] = None
    rule_name: Optional[str] = None
    claim_id: Optional[int] = None
    dimension_code: str
    severity_code: str
    current_status_code: str
    assigned_to_user: Optional[str] = None
    detected_at: str
    resolved_at: Optional[str] = None
    root_cause_code: Optional[str] = None
    variance_amount: Optional[str] = None

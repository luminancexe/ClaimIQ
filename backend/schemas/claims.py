"""Pydantic v2 schemas for claims endpoints."""

from typing import Optional, List
from pydantic import BaseModel


class ClaimLineSchema(BaseModel):
    """Single claim line item."""
    claim_line_id: int
    claim_id: int
    line_number: int
    cpt_code: str
    procedure_description: Optional[str] = None
    units: str  # Decimal as string
    unit_price: str  # Decimal as string
    line_billed_amount: str  # Decimal as string
    line_status: str


class StatusHistoryEntry(BaseModel):
    """Claim status transition history record."""
    history_id: int
    claim_id: int
    previous_status_code: Optional[str] = None
    new_status_code: str
    transition_timestamp: str
    transition_reason: Optional[str] = None
    actor_reference: str


class ClaimSummary(BaseModel):
    """Claim list item (paginated results)."""
    claim_id: int
    claim_reference: str
    encounter_id: int
    patient_id: int
    billing_provider_id: int
    payer_id: int
    current_status_code: str
    total_billed_amount: str  # Decimal as string
    submission_date: str
    adjudication_date: Optional[str] = None
    is_reconciled: bool


class ClaimDetail(BaseModel):
    """Full claim detail with financial summary."""
    claim_id: int
    claim_reference: str
    encounter_id: int
    patient_id: int
    billing_provider_id: int
    payer_id: int
    current_status_code: str
    total_billed_amount: str
    submission_date: str
    adjudication_date: Optional[str] = None
    is_reconciled: bool
    lines: Optional[List[ClaimLineSchema]] = None
    total_paid: Optional[str] = None
    total_adjusted: Optional[str] = None
    total_denied: Optional[str] = None

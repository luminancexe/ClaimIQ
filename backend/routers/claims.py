"""Claims routes for ClaimIQ Phase 7 Backend API."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
import pymysql

from backend.schemas.common import PaginatedResponse
from backend.schemas.claims import ClaimSummary, ClaimDetail, ClaimLineSchema, StatusHistoryEntry
from backend.dependencies import get_db, get_current_user
from backend.services.claims import (
    get_claims,
    get_claim_by_id,
    get_claim_lines,
    get_claim_history,
)

router = APIRouter(prefix="/api/v1/claims", tags=["Claims"])


@router.get("", response_model=PaginatedResponse[ClaimSummary])
def list_claims(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, description="Page size (1-500)"),
    status: Optional[str] = Query(None, description="Filter by current_status_code"),
    claim_reference: Optional[str] = Query(None, description="Search claim reference"),
    payer_id: Optional[int] = Query(None, description="Filter by payer_id"),
    provider_id: Optional[int] = Query(None, description="Filter by billing_provider_id"),
    patient_id: Optional[int] = Query(None, description="Filter by patient_id"),
    start_date: Optional[str] = Query(None, description="Start submission date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End submission date (YYYY-MM-DD)"),
    is_reconciled: Optional[bool] = Query(None, description="Filter by reconciled flag"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve paginated list of healthcare claims with optional filters."""
    if not conn:
        return PaginatedResponse[ClaimSummary](
            page=page,
            page_size=page_size,
            total=0,
            total_pages=0,
            has_next=False,
            has_previous=False,
            items=[],
        )

    filters = {
        "status": status,
        "claim_reference": claim_reference,
        "payer_id": payer_id,
        "provider_id": provider_id,
        "patient_id": patient_id,
        "start_date": start_date,
        "end_date": end_date,
        "is_reconciled": is_reconciled,
    }

    total, items = get_claims(conn, page=page, page_size=page_size, filters=filters)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse[ClaimSummary](
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total_pages > 0,
        items=[ClaimSummary(**item) for item in items],
    )


@router.get("/{claim_id}", response_model=ClaimDetail)
def get_claim(
    claim_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve full detail for a specific claim."""
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with ID {claim_id} not found",
        )

    claim = get_claim_by_id(conn, claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with ID {claim_id} not found",
        )

    return ClaimDetail(**claim)


@router.get("/{claim_id}/lines", response_model=List[ClaimLineSchema])
def get_lines(
    claim_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve line items for a specific claim."""
    if not conn:
        return []

    lines = get_claim_lines(conn, claim_id)
    return [ClaimLineSchema(**line) for line in lines]


@router.get("/{claim_id}/history", response_model=List[StatusHistoryEntry])
def get_history(
    claim_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve lifecycle status history for a specific claim."""
    if not conn:
        return []

    history = get_claim_history(conn, claim_id)
    return [StatusHistoryEntry(**h) for h in history]

"""Issues routes for ClaimIQ Phase 7 Backend API."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
import pymysql

from backend.schemas.common import PaginatedResponse
from backend.schemas.issues import IssueSummary, IssueDetail
from backend.dependencies import get_db, get_current_user
from backend.services.issues import get_issues, get_issue_by_id

router = APIRouter(prefix="/api/v1/issues", tags=["Issues"])


@router.get("", response_model=PaginatedResponse[IssueSummary])
def list_issues(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, description="Page size (1-500)"),
    severity: Optional[str] = Query(None, description="Filter by severity_code (Critical, High, Medium, Low)"),
    dimension: Optional[str] = Query(None, description="Filter by dimension_code"),
    status: Optional[str] = Query(None, description="Filter by current_status_code"),
    rule_id: Optional[int] = Query(None, description="Filter by rule_id"),
    claim_id: Optional[int] = Query(None, description="Filter by claim_id"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve paginated QA defect issues with optional filters."""
    if not conn:
        return PaginatedResponse[IssueSummary](
            page=page,
            page_size=page_size,
            total=0,
            total_pages=0,
            has_next=False,
            has_previous=False,
            items=[],
        )

    filters = {
        "severity": severity,
        "dimension": dimension,
        "status": status,
        "rule_id": rule_id,
        "claim_id": claim_id,
    }
    total, items = get_issues(conn, page=page, page_size=page_size, filters=filters)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse[IssueSummary](
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total_pages > 0,
        items=[IssueSummary(**i) for i in items],
    )


@router.get("/{issue_id}", response_model=IssueDetail)
def get_issue(
    issue_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve full detail for a specific QA defect issue."""
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )

    issue = get_issue_by_id(conn, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )

    return IssueDetail(**issue)

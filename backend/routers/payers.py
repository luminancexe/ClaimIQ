"""Payer routes for ClaimIQ Phase 7 Backend API."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
import pymysql

from backend.schemas.common import PaginatedResponse
from backend.schemas.analytics import PayerScorecardResponse
from backend.dependencies import get_db, get_current_user
from backend.database import execute_query, execute_query_single, execute_count
from backend.services.analytics import get_payers

router = APIRouter(prefix="/api/v1/payers", tags=["Payers"])


class PayerDetail(BaseModel):
    """Insurance payer entity detail."""
    payer_id: int
    payer_reference: str
    payer_name: str
    payer_type: str
    timely_filing_days: int


@router.get("", response_model=PaginatedResponse[PayerDetail])
def list_payers(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, description="Page size (1-500)"),
    payer_type: Optional[str] = Query(None, description="Filter by payer type"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve paginated directory of insurance payers."""
    if not conn:
        return PaginatedResponse[PayerDetail](
            page=page,
            page_size=page_size,
            total=0,
            total_pages=0,
            has_next=False,
            has_previous=False,
            items=[],
        )

    where_clauses = ["1=1"]
    params: List[Any] = []
    if payer_type:
        where_clauses.append("payer_type = %s")
        params.append(payer_type)

    where_sql = " AND ".join(where_clauses)
    total = execute_count(conn, f"SELECT COUNT(*) FROM payers WHERE {where_sql}", tuple(params))
    offset = (page - 1) * page_size

    sql = f"""
        SELECT payer_id, payer_reference, payer_name, payer_type, timely_filing_days
        FROM payers
        WHERE {where_sql}
        ORDER BY payer_id ASC
        LIMIT %s OFFSET %s
    """
    rows = execute_query(conn, sql, tuple(params + [page_size, offset]))
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse[PayerDetail](
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total_pages > 0,
        items=[PayerDetail(**r) for r in rows],
    )


@router.get("/{payer_id}", response_model=PayerDetail)
def get_payer_detail(
    payer_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve detailed profile for a single payer."""
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payer {payer_id} not found",
        )

    sql = """
        SELECT payer_id, payer_reference, payer_name, payer_type, timely_filing_days
        FROM payers
        WHERE payer_id = %s
    """
    row = execute_query_single(conn, sql, (payer_id,))
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payer {payer_id} not found",
        )
    return PayerDetail(**row)


@router.get("/{payer_id}/scorecard", response_model=PayerScorecardResponse)
def get_payer_scorecard(
    payer_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve adjudication efficiency scorecard for a specific payer."""
    data = get_payers(conn, payer_id=payer_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payer {payer_id} scorecard not found",
        )
    return PayerScorecardResponse(**data[0])

"""Provider routes for ClaimIQ Phase 7 Backend API."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
import pymysql

from backend.schemas.common import PaginatedResponse
from backend.schemas.analytics import ProviderScorecardResponse
from backend.dependencies import get_db, get_current_user
from backend.database import execute_query, execute_query_single, execute_count
from backend.services.analytics import get_providers

router = APIRouter(prefix="/api/v1/providers", tags=["Providers"])


class ProviderDetail(BaseModel):
    """Healthcare provider entity detail."""
    provider_id: int
    provider_reference: str
    facility_id: Optional[int] = None
    first_name: str
    last_name: str
    npi: str
    taxonomy_code: str
    specialty: str


@router.get("", response_model=PaginatedResponse[ProviderDetail])
def list_providers(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, description="Page size (1-500)"),
    specialty: Optional[str] = Query(None, description="Filter by provider specialty"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve paginated directory of healthcare providers."""
    if not conn:
        return PaginatedResponse[ProviderDetail](
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
    if specialty:
        where_clauses.append("specialty = %s")
        params.append(specialty)

    where_sql = " AND ".join(where_clauses)
    total = execute_count(conn, f"SELECT COUNT(*) FROM providers WHERE {where_sql}", tuple(params))
    offset = (page - 1) * page_size

    sql = f"""
        SELECT provider_id, provider_reference, facility_id, first_name,
               last_name, npi, taxonomy_code, specialty
        FROM providers
        WHERE {where_sql}
        ORDER BY provider_id ASC
        LIMIT %s OFFSET %s
    """
    rows = execute_query(conn, sql, tuple(params + [page_size, offset]))
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse[ProviderDetail](
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total_pages > 0,
        items=[ProviderDetail(**r) for r in rows],
    )


@router.get("/{provider_id}", response_model=ProviderDetail)
def get_provider_detail(
    provider_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve detailed profile for a single provider."""
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_id} not found",
        )

    sql = """
        SELECT provider_id, provider_reference, facility_id, first_name,
               last_name, npi, taxonomy_code, specialty
        FROM providers
        WHERE provider_id = %s
    """
    row = execute_query_single(conn, sql, (provider_id,))
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_id} not found",
        )
    return ProviderDetail(**row)


@router.get("/{provider_id}/scorecard", response_model=ProviderScorecardResponse)
def get_provider_scorecard(
    provider_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve quality scorecard for a specific provider."""
    data = get_providers(conn, provider_id=provider_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_id} scorecard not found",
        )
    return ProviderScorecardResponse(**data[0])

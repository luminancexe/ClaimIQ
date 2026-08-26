"""QA routes for ClaimIQ Phase 7 Backend API."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
import pymysql

from backend.schemas.common import PaginatedResponse
from backend.schemas.qa import (
    QARuleSchema,
    QARunSchema,
    QAResultSchema,
    DQScoreSchema,
)
from backend.schemas.issues import IssueSummary
from backend.dependencies import get_db, get_current_user
from backend.services.qa import (
    get_rules,
    get_rule_by_id,
    get_runs,
    get_run_by_id,
    get_results,
    get_dq_scores,
)
from backend.services.issues import get_issues

router = APIRouter(prefix="/api/v1/qa", tags=["QA"])


@router.get("/rules", response_model=List[QARuleSchema])
def list_rules(
    category: Optional[str] = Query(None, description="Filter by category code"),
    dimension: Optional[str] = Query(None, description="Filter by dimension code"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve all 67 QA rule definitions."""
    rules = get_rules(conn, category=category, dimension=dimension)
    return [QARuleSchema(**r) for r in rules]


@router.get("/rules/{rule_id}", response_model=QARuleSchema)
def get_rule_detail(
    rule_id: str,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve a single QA rule by rule_id or rule_code (e.g. 'R-E001' or '1')."""
    rule = get_rule_by_id(conn, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QA Rule '{rule_id}' not found",
        )
    return QARuleSchema(**rule)


@router.get("/runs", response_model=PaginatedResponse[QARunSchema])
def list_runs(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, description="Page size (1-500)"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve paginated QA execution runs."""
    if not conn:
        return PaginatedResponse[QARunSchema](
            page=page,
            page_size=page_size,
            total=0,
            total_pages=0,
            has_next=False,
            has_previous=False,
            items=[],
        )

    total, items = get_runs(conn, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse[QARunSchema](
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total_pages > 0,
        items=[QARunSchema(**i) for i in items],
    )


@router.get("/runs/{run_id}", response_model=QARunSchema)
def get_run_detail(
    run_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve summary detail for a specific QA run."""
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QA Run {run_id} not found",
        )

    run = get_run_by_id(conn, run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"QA Run {run_id} not found",
        )
    return QARunSchema(**run)


@router.get("/results", response_model=List[QAResultSchema])
def list_results(
    run_id: Optional[int] = Query(None, description="Filter results by run_id"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve per-rule execution results for a QA run."""
    if not conn:
        return []

    results = get_results(conn, run_id=run_id)
    return [QAResultSchema(**r) for r in results]


@router.get("/scores", response_model=DQScoreSchema)
def get_scores(
    run_id: Optional[int] = Query(None, description="Run ID (defaults to latest)"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve 7-dimension weighted Data Quality score summary."""
    if not conn:
        return DQScoreSchema(
            run_id=None,
            overall_dq_score=100.0,
            total_records_evaluated=0,
            total_issues_detected=0,
            dimension_scores={},
            severity_breakdown={"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
        )

    scores = get_dq_scores(conn, run_id=run_id)
    return DQScoreSchema(**scores)


@router.get("/issues", response_model=PaginatedResponse[IssueSummary])
def list_qa_issues(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, description="Page size (1-500)"),
    severity: Optional[str] = Query(None, description="Filter by severity_code"),
    dimension: Optional[str] = Query(None, description="Filter by dimension_code"),
    status: Optional[str] = Query(None, description="Filter by current_status_code"),
    rule_id: Optional[int] = Query(None, description="Filter by rule_id"),
    claim_id: Optional[int] = Query(None, description="Filter by claim_id"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve QA defect issues."""
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

"""Analytics routes for ClaimIQ Phase 7 Backend API."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
import pymysql

from backend.schemas.analytics import (
    AnalyticsOverviewResponse,
    FinancialOverview,
    KPIResponse,
    TrendResponse,
    RootCauseResponse,
    RecurrenceResponse,
    ProviderScorecardResponse,
    PayerScorecardResponse,
)
from backend.dependencies import get_db, get_current_user
from backend.services.analytics import (
    get_overview,
    get_financial,
    get_kpis,
    get_providers,
    get_payers,
    get_trends,
    get_root_causes,
    get_recurrence,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def analytics_overview(
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve comprehensive analytics overview (financial + KPIs + root causes)."""
    data = get_overview(conn)
    return AnalyticsOverviewResponse(**data)


@router.get("/financial", response_model=FinancialOverview)
def financial_analytics(
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve financial exposure, variance rollups, and reconciliation metrics."""
    data = get_financial(conn)
    return FinancialOverview(**data)


@router.get("/kpis", response_model=KPIResponse)
def operational_kpis(
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve operational KPIs (claims, payments, denials, QA)."""
    data = get_kpis(conn)
    return KPIResponse(**data)


@router.get("/providers", response_model=List[ProviderScorecardResponse])
def provider_analytics(
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve quality and financial scorecards for all healthcare providers."""
    data = get_providers(conn)
    return [ProviderScorecardResponse(**p) for p in data]


@router.get("/providers/{provider_id}", response_model=ProviderScorecardResponse)
def provider_scorecard(
    provider_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve scorecard for a specific healthcare provider."""
    data = get_providers(conn, provider_id=provider_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_id} scorecard not found",
        )
    return ProviderScorecardResponse(**data[0])


@router.get("/payers", response_model=List[PayerScorecardResponse])
def payer_analytics(
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve adjudication efficiency scorecards for all insurance payers."""
    data = get_payers(conn)
    return [PayerScorecardResponse(**p) for p in data]


@router.get("/payers/{payer_id}", response_model=PayerScorecardResponse)
def payer_scorecard(
    payer_id: int,
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve scorecard for a specific insurance payer."""
    data = get_payers(conn, payer_id=payer_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payer {payer_id} scorecard not found",
        )
    return PayerScorecardResponse(**data[0])


@router.get("/trends", response_model=TrendResponse)
def dq_trends(
    interval: str = Query("monthly", description="Trend interval: daily, weekly, monthly"),
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve longitudinal Data Quality score trends and trajectory."""
    if interval not in ("daily", "weekly", "monthly"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid trend interval. Allowed: daily, weekly, monthly",
        )
    data = get_trends(conn, interval=interval)
    return TrendResponse(**data)


@router.get("/root-causes", response_model=RootCauseResponse)
def root_cause_analytics(
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve Pareto 80/20 root cause defect concentration analysis."""
    data = get_root_causes(conn)
    return RootCauseResponse(**data)


@router.get("/recurrence", response_model=RecurrenceResponse)
def recurrence_analytics(
    conn: Optional[pymysql.Connection] = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Retrieve repeat offender and recurring defect pattern clusters."""
    data = get_recurrence(conn)
    return RecurrenceResponse(**data)

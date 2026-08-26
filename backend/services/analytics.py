"""Analytics service delegating directly to ClaimIQ Phase 6 Analytics Engine."""

from typing import Optional, Dict, Any, List
import pymysql

from analytics.config import AnalyticsConfig
from analytics.financial import calculate_financial_exposure
from analytics.kpis import calculate_kpi_overview
from analytics.scorecards import generate_provider_scorecards, generate_payer_scorecards
from analytics.trends import calculate_dq_trends
from analytics.root_cause import calculate_root_cause_distribution
from analytics.recurrence import calculate_recurrence_patterns


def get_financial(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> Dict[str, Any]:
    """Calculate and return financial exposure summary."""
    cfg = config or AnalyticsConfig()
    result = calculate_financial_exposure(conn, cfg)
    return result.to_dict()


def get_kpis(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> Dict[str, Any]:
    """Calculate and return operational KPIs."""
    cfg = config or AnalyticsConfig()
    result = calculate_kpi_overview(conn, cfg)
    return result.to_dict()


def get_providers(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
    provider_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Generate and return provider quality scorecards."""
    cfg = config or AnalyticsConfig()
    cards = generate_provider_scorecards(conn, cfg)
    results = [c.to_dict() for c in cards]
    if provider_id is not None:
        results = [c for c in results if c["provider_id"] == provider_id]
    return results


def get_payers(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
    payer_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Generate and return payer adjudication scorecards."""
    cfg = config or AnalyticsConfig()
    cards = generate_payer_scorecards(conn, cfg)
    results = [c.to_dict() for c in cards]
    if payer_id is not None:
        results = [c for c in results if c["payer_id"] == payer_id]
    return results


def get_trends(
    conn: Optional[pymysql.Connection],
    interval: str = "monthly",
    config: Optional[AnalyticsConfig] = None,
) -> Dict[str, Any]:
    """Calculate and return DQ time-series trends."""
    cfg = config or AnalyticsConfig(trend_interval=interval)
    cfg.trend_interval = interval
    result = calculate_dq_trends(conn, cfg)
    return result.to_dict()


def get_root_causes(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> Dict[str, Any]:
    """Calculate and return Pareto 80/20 root cause distribution."""
    cfg = config or AnalyticsConfig()
    result = calculate_root_cause_distribution(conn, cfg)
    return result.to_dict()


def get_recurrence(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> Dict[str, Any]:
    """Calculate and return recurring defect clusters."""
    cfg = config or AnalyticsConfig()
    result = calculate_recurrence_patterns(conn, cfg)
    return result.to_dict()


def get_overview(
    conn: Optional[pymysql.Connection],
    config: Optional[AnalyticsConfig] = None,
) -> Dict[str, Any]:
    """Return aggregated overview combining financial, KPIs, and root causes."""
    cfg = config or AnalyticsConfig()
    return {
        "financial": get_financial(conn, cfg),
        "kpis": get_kpis(conn, cfg),
        "root_cause": get_root_causes(conn, cfg),
    }

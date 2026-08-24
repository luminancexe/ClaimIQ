"""Core Analytics Execution Engine for ClaimIQ Phase 6."""

import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import pymysql

from analytics.config import AnalyticsConfig
from analytics.models import (
    FinancialExposureSummary,
    KPIOverview,
    ProviderScorecard,
    PayerScorecard,
    DQTrendsSummary,
    RootCauseDistribution,
    RecurrenceSummary,
    AnalyticsRunTelemetry,
    AnalyticsReport,
)
from analytics.database import get_analytics_connection
from analytics.financial import calculate_financial_exposure
from analytics.kpis import calculate_kpi_overview
from analytics.scorecards import generate_provider_scorecards, generate_payer_scorecards
from analytics.trends import calculate_dq_trends
from analytics.root_cause import calculate_root_cause_distribution
from analytics.recurrence import calculate_recurrence_patterns


class AnalyticsExecutionEngine:
    """Deterministic, read-only analytics execution engine for ClaimIQ claims and QA data."""

    def __init__(self, config: AnalyticsConfig):
        self.config = config

    def execute(self) -> AnalyticsReport:
        """Orchestrate analytics calculation based on configured report filters."""
        start_perf = time.perf_counter()
        now_dt = datetime.now(timezone.utc)
        report_id = f"ANL-REP-{now_dt.strftime('%Y%m%d-%H%M%S')}"

        conn: Optional[pymysql.Connection] = None
        try:
            conn = get_analytics_connection(self.config)
        except Exception:
            if not self.config.dry_run:
                raise

        financial_res: Optional[FinancialExposureSummary] = None
        kpis_res: Optional[KPIOverview] = None
        providers_res: Optional[List[ProviderScorecard]] = None
        payers_res: Optional[List[PayerScorecard]] = None
        trends_res: Optional[DQTrendsSummary] = None
        root_cause_res: Optional[RootCauseDistribution] = None
        recurrence_res: Optional[RecurrenceSummary] = None

        rep_type = self.config.report_type.lower()

        try:
            if rep_type in ("all", "financial", "overview"):
                financial_res = calculate_financial_exposure(conn, self.config)

            if rep_type in ("all", "kpis", "overview"):
                kpis_res = calculate_kpi_overview(conn, self.config)

            if rep_type in ("all", "provider"):
                providers_res = generate_provider_scorecards(conn, self.config)

            if rep_type in ("all", "payer"):
                payers_res = generate_payer_scorecards(conn, self.config)

            if rep_type in ("all", "trends"):
                trends_res = calculate_dq_trends(conn, self.config)

            if rep_type in ("all", "root-cause", "overview"):
                root_cause_res = calculate_root_cause_distribution(conn, self.config)

            if rep_type in ("all", "recurrence"):
                recurrence_res = calculate_recurrence_patterns(conn, self.config)

            elapsed_ms = int((time.perf_counter() - start_perf) * 1000)
            scanned_records = 0
            if kpis_res:
                scanned_records = kpis_res.claims.total_claims

            telemetry = AnalyticsRunTelemetry(
                report_type=self.config.report_type,
                execution_duration_ms=elapsed_ms,
                records_scanned=scanned_records,
                executed_at=now_dt.isoformat(),
                status="SUCCESS",
            )

            return AnalyticsReport(
                report_id=report_id,
                generated_at=now_dt.isoformat(),
                batch_identifier=self.config.batch_identifier,
                config=self.config.to_dict(),
                financial=financial_res,
                kpis=kpis_res,
                provider_scorecards=providers_res,
                payer_scorecards=payers_res,
                dq_trends=trends_res,
                root_cause=root_cause_res,
                recurrence=recurrence_res,
                telemetry=telemetry,
            )

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

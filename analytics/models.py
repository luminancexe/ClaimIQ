"""Strongly typed dataclasses and result models for ClaimIQ Analytics Engine."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional, Any


@dataclass
class FinancialExposureSummary:
    """Comprehensive financial exposure and reconciliation integrity metrics."""
    total_billed: Decimal
    total_paid: Decimal
    total_contractual_adjustments: Decimal
    total_patient_responsibility: Decimal
    total_variance: Decimal
    unreconciled_amount: Decimal
    overpayment_exposure: Decimal
    underpayment_exposure: Decimal
    total_denied_amount: Decimal
    reconciliation_rate: float  # (reconciled eligible claims / eligible claims) * 100
    payment_rate: float         # (total_paid / total_billed) * 100
    financial_integrity_rate: float  # 100 - (abs_variance / total_billed * 100)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_billed": str(self.total_billed),
            "total_paid": str(self.total_paid),
            "total_contractual_adjustments": str(self.total_contractual_adjustments),
            "total_patient_responsibility": str(self.total_patient_responsibility),
            "total_variance": str(self.total_variance),
            "unreconciled_amount": str(self.unreconciled_amount),
            "overpayment_exposure": str(self.overpayment_exposure),
            "underpayment_exposure": str(self.underpayment_exposure),
            "total_denied_amount": str(self.total_denied_amount),
            "reconciliation_rate": round(self.reconciliation_rate, 2),
            "payment_rate": round(self.payment_rate, 2),
            "financial_integrity_rate": round(self.financial_integrity_rate, 2),
        }


@dataclass
class ClaimsKPIOverview:
    """Claims operational metrics and status distribution."""
    total_claims: int
    status_distribution: Dict[str, int]
    adjudicated_claims: int
    adjudication_rate: float  # (adjudicated / total) * 100
    reconciled_claims: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_claims": self.total_claims,
            "status_distribution": self.status_distribution,
            "adjudicated_claims": self.adjudicated_claims,
            "adjudication_rate": round(self.adjudication_rate, 2),
            "reconciled_claims": self.reconciled_claims,
        }


@dataclass
class PaymentKPIOverview:
    """Disbursement volumes, payment averages, and velocity."""
    total_payments_count: int
    total_paid_amount: Decimal
    average_payment_amount: Decimal
    zero_payment_count: int
    average_payment_turnaround_days: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_payments_count": self.total_payments_count,
            "total_paid_amount": str(self.total_paid_amount),
            "average_payment_amount": str(self.average_payment_amount),
            "zero_payment_count": self.zero_payment_count,
            "average_payment_turnaround_days": round(self.average_payment_turnaround_days, 2) if self.average_payment_turnaround_days is not None else None,
        }


@dataclass
class DenialKPIOverview:
    """Denial rates, appealability, and top denial reason codes."""
    total_denials: int
    denial_rate: float  # (denials / adjudicated claims) * 100
    appealable_rate: float  # (appealable denials / total denials) * 100
    top_denial_reasons: List[Dict[str, Any]]
    denial_financial_exposure: Decimal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_denials": self.total_denials,
            "denial_rate": round(self.denial_rate, 2),
            "appealable_rate": round(self.appealable_rate, 2),
            "top_denial_reasons": self.top_denial_reasons,
            "denial_financial_exposure": str(self.denial_financial_exposure),
        }


@dataclass
class QAKPIOverview:
    """Quality assurance metrics and defect density."""
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_dimension: Dict[str, int]
    average_dq_score: float
    clean_record_rate: float  # (claims without issues / total claims) * 100
    defect_density: float     # total issues / total claims

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_issues": self.total_issues,
            "issues_by_severity": self.issues_by_severity,
            "issues_by_dimension": self.issues_by_dimension,
            "average_dq_score": round(self.average_dq_score, 2),
            "clean_record_rate": round(self.clean_record_rate, 2),
            "defect_density": round(self.defect_density, 4),
        }


@dataclass
class KPIOverview:
    """Aggregated operational KPI container."""
    claims: ClaimsKPIOverview
    payments: PaymentKPIOverview
    denials: DenialKPIOverview
    qa: QAKPIOverview

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claims": self.claims.to_dict(),
            "payments": self.payments.to_dict(),
            "denials": self.denials.to_dict(),
            "qa": self.qa.to_dict(),
        }


@dataclass
class ProviderScorecard:
    """Quality, volume, and financial performance scorecard for a healthcare provider."""
    provider_id: int
    provider_reference: str
    provider_name: str
    specialty: str
    facility_id: Optional[int]
    facility_name: Optional[str]
    claim_volume: int
    total_billed: Decimal
    total_paid: Decimal
    payment_rate: float
    denial_rate: float
    issue_count: int
    issue_density: float
    dq_score: float
    financial_exposure: Decimal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_reference": self.provider_reference,
            "provider_name": self.provider_name,
            "specialty": self.specialty,
            "facility_id": self.facility_id,
            "facility_name": self.facility_name,
            "claim_volume": self.claim_volume,
            "total_billed": str(self.total_billed),
            "total_paid": str(self.total_paid),
            "payment_rate": round(self.payment_rate, 2),
            "denial_rate": round(self.denial_rate, 2),
            "issue_count": self.issue_count,
            "issue_density": round(self.issue_density, 4),
            "dq_score": round(self.dq_score, 2),
            "financial_exposure": str(self.financial_exposure),
        }


@dataclass
class PayerScorecard:
    """Adjudication efficiency, turnaround velocity, and denial scorecard for an insurance payer."""
    payer_id: int
    payer_reference: str
    payer_name: str
    payer_type: str
    claim_volume: int
    total_billed: Decimal
    total_paid: Decimal
    denial_rate: float
    payment_rate: float
    average_adjudication_latency_days: float
    average_payment_latency_days: float
    timely_filing_compliance_rate: float
    contractual_adjustment_ratio: float
    issue_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payer_id": self.payer_id,
            "payer_reference": self.payer_reference,
            "payer_name": self.payer_name,
            "payer_type": self.payer_type,
            "claim_volume": self.claim_volume,
            "total_billed": str(self.total_billed),
            "total_paid": str(self.total_paid),
            "denial_rate": round(self.denial_rate, 2),
            "payment_rate": round(self.payment_rate, 2),
            "average_adjudication_latency_days": round(self.average_adjudication_latency_days, 2),
            "average_payment_latency_days": round(self.average_payment_latency_days, 2),
            "timely_filing_compliance_rate": round(self.timely_filing_compliance_rate, 2),
            "contractual_adjustment_ratio": round(self.contractual_adjustment_ratio, 2),
            "issue_count": self.issue_count,
        }


@dataclass
class DQTrendPoint:
    """A discrete time bucket point in longitudinal DQ trend series."""
    time_bucket: str  # YYYY-MM, YYYY-Www, or YYYY-MM-DD
    overall_dq_score: float
    dimension_scores: Dict[str, float]
    issue_count: int
    claim_volume: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_bucket": self.time_bucket,
            "overall_dq_score": round(self.overall_dq_score, 2),
            "dimension_scores": {k: round(v, 2) for k, v in self.dimension_scores.items()},
            "issue_count": self.issue_count,
            "claim_volume": self.claim_volume,
        }


@dataclass
class DQTrendsSummary:
    """Longitudinal time-series DQ trend analysis and score trajectory."""
    interval: str  # daily, weekly, monthly
    points: List[DQTrendPoint]
    rolling_average_score: float
    score_velocity: float  # Delta score per bucket
    trend_direction: str   # IMPROVING, STABLE, DEGRADING

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interval": self.interval,
            "points": [p.to_dict() for p in self.points],
            "rolling_average_score": round(self.rolling_average_score, 2),
            "score_velocity": round(self.score_velocity, 4),
            "trend_direction": self.trend_direction,
        }


@dataclass
class RootCauseItem:
    """Individual anomaly / rule root cause contribution in Pareto ranking."""
    anomaly_category: str
    anomaly_code: str
    rule_code: str
    description: str
    severity_code: str
    dimension_code: str
    issue_count: int
    percentage_of_total: float
    cumulative_percentage: float
    financial_exposure: Decimal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_category": self.anomaly_category,
            "anomaly_code": self.anomaly_code,
            "rule_code": self.rule_code,
            "description": self.description,
            "severity_code": self.severity_code,
            "dimension_code": self.dimension_code,
            "issue_count": self.issue_count,
            "percentage_of_total": round(self.percentage_of_total, 2),
            "cumulative_percentage": round(self.cumulative_percentage, 2),
            "financial_exposure": str(self.financial_exposure),
        }


@dataclass
class RootCauseDistribution:
    """Pareto 80/20 defect concentration and primary driver analysis."""
    items: List[RootCauseItem]
    pareto_cutoff_index: int  # 0-indexed count of items accounting for >= 80%
    primary_defect_driver: str
    total_issues_analyzed: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [i.to_dict() for i in self.items],
            "pareto_cutoff_index": self.pareto_cutoff_index,
            "primary_defect_driver": self.primary_defect_driver,
            "total_issues_analyzed": self.total_issues_analyzed,
        }


@dataclass
class RecurrencePattern:
    """Repeated defect pattern clustered across entities or rule categories."""
    entity_type: str  # PROVIDER, PAYER, PATIENT, CPT_CODE, RULE
    entity_identifier: str
    anomaly_code: str
    occurrence_count: int
    first_detected_at: Optional[str]
    last_detected_at: Optional[str]
    recurrence_rank: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "entity_identifier": self.entity_identifier,
            "anomaly_code": self.anomaly_code,
            "occurrence_count": self.occurrence_count,
            "first_detected_at": self.first_detected_at,
            "last_detected_at": self.last_detected_at,
            "recurrence_rank": self.recurrence_rank,
        }


@dataclass
class RecurrenceSummary:
    """Summary of recurring defect clusters and repeat offender rates."""
    recurring_cluster_count: int
    top_repeat_entities: List[RecurrencePattern]
    repeat_issue_rate: float  # (repeat occurrences / total issues) * 100
    total_repeating_occurrences: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recurring_cluster_count": self.recurring_cluster_count,
            "top_repeat_entities": [e.to_dict() for e in self.top_repeat_entities],
            "repeat_issue_rate": round(self.repeat_issue_rate, 2),
            "total_repeating_occurrences": self.total_repeating_occurrences,
        }


@dataclass
class AnalyticsRunTelemetry:
    """Execution latency and record telemetry for an analytics run."""
    report_type: str
    execution_duration_ms: int
    records_scanned: int
    executed_at: str
    status: str = "SUCCESS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_type": self.report_type,
            "execution_duration_ms": self.execution_duration_ms,
            "records_scanned": self.records_scanned,
            "executed_at": self.executed_at,
            "status": self.status,
        }


@dataclass
class AnalyticsReport:
    """Comprehensive analytical report container aggregating all module results."""
    report_id: str
    generated_at: str
    batch_identifier: Optional[str]
    config: Dict[str, Any]
    financial: Optional[FinancialExposureSummary] = None
    kpis: Optional[KPIOverview] = None
    provider_scorecards: Optional[List[ProviderScorecard]] = None
    payer_scorecards: Optional[List[PayerScorecard]] = None
    dq_trends: Optional[DQTrendsSummary] = None
    root_cause: Optional[RootCauseDistribution] = None
    recurrence: Optional[RecurrenceSummary] = None
    telemetry: Optional[AnalyticsRunTelemetry] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "batch_identifier": self.batch_identifier,
            "config": self.config,
            "financial": self.financial.to_dict() if self.financial else None,
            "kpis": self.kpis.to_dict() if self.kpis else None,
            "provider_scorecards": [s.to_dict() for s in self.provider_scorecards] if self.provider_scorecards is not None else None,
            "payer_scorecards": [s.to_dict() for s in self.payer_scorecards] if self.payer_scorecards is not None else None,
            "dq_trends": self.dq_trends.to_dict() if self.dq_trends else None,
            "root_cause": self.root_cause.to_dict() if self.root_cause else None,
            "recurrence": self.recurrence.to_dict() if self.recurrence else None,
            "telemetry": self.telemetry.to_dict() if self.telemetry else None,
        }

"""Pydantic v2 schemas for analytics endpoints."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class FinancialOverview(BaseModel):
    """Financial exposure and reconciliation integrity response."""
    total_billed: str
    total_paid: str
    total_contractual_adjustments: str
    total_patient_responsibility: str
    total_variance: str
    unreconciled_amount: str
    overpayment_exposure: str
    underpayment_exposure: str
    total_denied_amount: str
    reconciliation_rate: float
    payment_rate: float
    financial_integrity_rate: float


class ClaimsKPISchema(BaseModel):
    """Claims operational KPI metrics."""
    total_claims: int
    status_distribution: Dict[str, int]
    adjudicated_claims: int
    adjudication_rate: float
    reconciled_claims: int


class PaymentKPISchema(BaseModel):
    """Payment volume and velocity KPIs."""
    total_payments_count: int
    total_paid_amount: str
    average_payment_amount: str
    zero_payment_count: int
    average_payment_turnaround_days: Optional[float] = None


class DenialKPISchema(BaseModel):
    """Denial rates and top reasons."""
    total_denials: int
    denial_rate: float
    appealable_rate: float
    top_denial_reasons: List[Dict[str, Any]]
    denial_financial_exposure: str


class QAKPISchema(BaseModel):
    """QA defect density and quality metrics."""
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_dimension: Dict[str, int]
    average_dq_score: float
    clean_record_rate: float
    defect_density: float


class KPIResponse(BaseModel):
    """Aggregated operational KPI container."""
    claims: ClaimsKPISchema
    payments: PaymentKPISchema
    denials: DenialKPISchema
    qa: QAKPISchema


class TrendPointSchema(BaseModel):
    """Single time-series data point."""
    time_bucket: str
    overall_dq_score: float
    dimension_scores: Dict[str, float]
    issue_count: int
    claim_volume: int


class TrendResponse(BaseModel):
    """DQ score time-series trend analysis."""
    interval: str
    points: List[TrendPointSchema]
    rolling_average_score: float
    score_velocity: float
    trend_direction: str


class RootCauseItemSchema(BaseModel):
    """Individual Pareto root cause item."""
    anomaly_category: str
    anomaly_code: str
    rule_code: str
    description: str
    severity_code: str
    dimension_code: str
    issue_count: int
    percentage_of_total: float
    cumulative_percentage: float
    financial_exposure: str


class RootCauseResponse(BaseModel):
    """Pareto 80/20 defect concentration analysis."""
    items: List[RootCauseItemSchema]
    pareto_cutoff_index: int
    primary_defect_driver: str
    total_issues_analyzed: int


class RecurrencePatternSchema(BaseModel):
    """Repeat defect pattern cluster."""
    entity_type: str
    entity_identifier: str
    anomaly_code: str
    occurrence_count: int
    first_detected_at: Optional[str] = None
    last_detected_at: Optional[str] = None
    recurrence_rank: int


class RecurrenceResponse(BaseModel):
    """Recurrence pattern clustering summary."""
    recurring_cluster_count: int
    top_repeat_entities: List[RecurrencePatternSchema]
    repeat_issue_rate: float
    total_repeating_occurrences: int


class ProviderScorecardResponse(BaseModel):
    """Provider quality and financial performance scorecard."""
    provider_id: int
    provider_reference: str
    provider_name: str
    specialty: str
    facility_id: Optional[int] = None
    facility_name: Optional[str] = None
    claim_volume: int
    total_billed: str
    total_paid: str
    payment_rate: float
    denial_rate: float
    issue_count: int
    issue_density: float
    dq_score: float
    financial_exposure: str


class PayerScorecardResponse(BaseModel):
    """Payer adjudication efficiency scorecard."""
    payer_id: int
    payer_reference: str
    payer_name: str
    payer_type: str
    claim_volume: int
    total_billed: str
    total_paid: str
    denial_rate: float
    payment_rate: float
    average_adjudication_latency_days: float
    average_payment_latency_days: float
    timely_filing_compliance_rate: float
    contractual_adjustment_ratio: float
    issue_count: int


class AnalyticsOverviewResponse(BaseModel):
    """Combined analytics overview (financial + KPIs + root causes)."""
    financial: Optional[FinancialOverview] = None
    kpis: Optional[KPIResponse] = None
    root_cause: Optional[RootCauseResponse] = None

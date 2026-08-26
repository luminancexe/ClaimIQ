"""Pydantic v2 schemas for QA engine endpoints."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class QARuleSchema(BaseModel):
    """QA rule definition."""
    rule_id: Optional[int] = None
    rule_code: str
    category_code: Optional[str] = None
    category_id: Optional[int] = None
    dimension_code: str
    default_severity_code: str
    rule_name: str
    description: str
    detection_method: Optional[str] = None
    is_active: bool = True


class QARunSchema(BaseModel):
    """QA execution run summary."""
    run_id: int
    run_reference: str
    batch_identifier: str
    started_at: str
    completed_at: Optional[str] = None
    status: str
    total_rules_evaluated: int
    total_records_evaluated: int
    total_issues_detected: int
    dq_score: Optional[str] = None  # Decimal as string


class QAResultSchema(BaseModel):
    """Per-rule QA execution result within a run."""
    result_id: int
    run_id: int
    rule_id: int
    rule_code: Optional[str] = None
    records_evaluated: int
    issues_detected: int
    execution_duration_ms: int
    run_status: str


class DQDimensionScoreSchema(BaseModel):
    """Score breakdown for a single DQ dimension."""
    dimension_code: str
    dimension_name: str
    weight: float
    records_evaluated: int
    issues_detected: int
    raw_score: float
    weighted_score: float


class DQScoreSchema(BaseModel):
    """Data Quality score summary for a QA run."""
    run_id: Optional[int] = None
    overall_dq_score: float
    total_records_evaluated: int
    total_issues_detected: int
    dimension_scores: Dict[str, DQDimensionScoreSchema] = {}
    severity_breakdown: Dict[str, int] = {}

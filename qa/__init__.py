"""ClaimIQ Phase 5 — Data Quality & QA Rule Engine Package."""

from qa.config import QAConfig
from qa.models import (
    QARuleDefinition,
    QADetectionRecord,
    QARunTelemetry,
    DQScoreSummary,
    GroundTruthEvaluationResult,
)
from qa.registry import get_rule, list_all_rules, QA_RULE_REGISTRY
from qa.engine import QAExecutionEngine

__all__ = [
    "QAConfig",
    "QARuleDefinition",
    "QADetectionRecord",
    "QARunTelemetry",
    "DQScoreSummary",
    "GroundTruthEvaluationResult",
    "get_rule",
    "list_all_rules",
    "QA_RULE_REGISTRY",
    "QAExecutionEngine",
]

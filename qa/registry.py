"""Central QA Rule Registry and Taxonomy Index for ClaimIQ Phase 5."""

from typing import Dict, List, Optional
from qa.models import QARuleDefinition
from qa.rules import ALL_RULE_DEFINITIONS, RULE_EVALUATOR_MAP

QA_RULE_REGISTRY: Dict[str, QARuleDefinition] = {
    r.rule_code: r for r in ALL_RULE_DEFINITIONS
}

ANOMALY_TO_RULE_MAP: Dict[str, QARuleDefinition] = {}
for r in ALL_RULE_DEFINITIONS:
    for a_code in r.anomaly_codes:
        ANOMALY_TO_RULE_MAP[a_code] = r


def get_rule(rule_or_anomaly_code: str) -> QARuleDefinition:
    """Retrieve rule definition by rule_code (e.g. 'R-E023') or anomaly_code (e.g. 'E023')."""
    clean_code = rule_or_anomaly_code.strip().upper()
    if clean_code in QA_RULE_REGISTRY:
        return QA_RULE_REGISTRY[clean_code]
    if clean_code in ANOMALY_TO_RULE_MAP:
        return ANOMALY_TO_RULE_MAP[clean_code]
    raise KeyError(f"Unknown QA rule or anomaly code '{rule_or_anomaly_code}'.")


def get_rule_by_anomaly(anomaly_code: str) -> Optional[QARuleDefinition]:
    """Retrieve rule definition directly mapped to a specific anomaly code."""
    return ANOMALY_TO_RULE_MAP.get(anomaly_code.strip().upper())


def get_rules_by_category(category_code: str) -> List[QARuleDefinition]:
    """Retrieve all active QA rules within a specific category."""
    cat = category_code.strip().upper()
    return [r for r in ALL_RULE_DEFINITIONS if r.category_code == cat]


def get_rules_by_dimension(dimension_code: str) -> List[QARuleDefinition]:
    """Retrieve all active QA rules within a specific DQ dimension."""
    dim = dimension_code.strip().lower()
    return [r for r in ALL_RULE_DEFINITIONS if r.dimension_code.lower() == dim]


def list_all_rules() -> List[QARuleDefinition]:
    """Return an ordered list of all registered QA rules."""
    return list(ALL_RULE_DEFINITIONS)

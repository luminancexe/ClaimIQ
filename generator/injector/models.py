"""Data models for ClaimIQ Phase 4 Anomaly Injection & Ground Truth."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any


class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AnomalyCategory(str, Enum):
    COMPLETENESS = "Completeness"
    DUPLICATION = "Duplication / Uniqueness"
    REFERENTIAL = "Referential / Cross-Entity"
    FINANCIAL = "Financial / Reconciliation"
    TEMPORAL = "Temporal"
    LIFECYCLE = "Claim Lifecycle / FSM"
    BUSINESS_LOGIC = "Business Logic / Operational"
    FORMATTING = "Code / Formatting"


@dataclass(frozen=True)
class AnomalyDefinition:
    code: str
    category: AnomalyCategory
    name: str
    description: str
    severity: SeverityLevel
    target_table: str
    target_column: str
    expected_rule_category: str
    mutation_strategy: str
    expected_violation: str
    is_reversible: bool = True
    is_database_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "category": self.category.value,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "target_table": self.target_table,
            "target_column": self.target_column,
            "expected_rule_category": self.expected_rule_category,
            "mutation_strategy": self.mutation_strategy,
            "expected_violation": self.expected_violation,
            "is_reversible": self.is_reversible,
            "is_database_safe": self.is_database_safe,
        }


@dataclass
class GroundTruthRecord:
    anomaly_code: str
    category_name: str
    severity_code: str
    target_table: str
    target_record_id: int
    target_column: str
    original_value: Optional[str]
    mutated_value: Optional[str]
    injection_profile: str
    injection_seed: int
    description: str
    expected_rule_category: str
    target_business_reference: Optional[str] = None
    injected_at: Optional[str] = None
    is_active: bool = True
    ground_truth_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ground_truth_id": self.ground_truth_id,
            "anomaly_code": self.anomaly_code,
            "category_name": self.category_name,
            "severity_code": self.severity_code,
            "target_table": self.target_table,
            "target_record_id": self.target_record_id,
            "target_business_reference": self.target_business_reference,
            "target_column": self.target_column,
            "original_value": self.original_value,
            "mutated_value": self.mutated_value,
            "injection_profile": self.injection_profile,
            "injection_seed": self.injection_seed,
            "description": self.description,
            "expected_rule_category": self.expected_rule_category,
            "injected_at": self.injected_at,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GroundTruthRecord":
        return cls(
            ground_truth_id=data.get("ground_truth_id"),
            anomaly_code=data["anomaly_code"],
            category_name=data["category_name"],
            severity_code=data["severity_code"],
            target_table=data["target_table"],
            target_record_id=data["target_record_id"],
            target_business_reference=data.get("target_business_reference"),
            target_column=data["target_column"],
            original_value=data.get("original_value"),
            mutated_value=data.get("mutated_value"),
            injection_profile=data["injection_profile"],
            injection_seed=data["injection_seed"],
            description=data["description"],
            expected_rule_category=data["expected_rule_category"],
            injected_at=data.get("injected_at"),
            is_active=data.get("is_active", True),
        )

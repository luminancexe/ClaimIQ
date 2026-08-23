"""Injection Profile Definitions and Targeting Configurations for ClaimIQ Phase 4."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from generator.injector.taxonomy import TAXONOMY


@dataclass
class InjectionProfileConfig:
    name: str
    target_rate: float  # Percentage of target population to mutate (0.0 to 1.0)
    default_count_per_anomaly: int
    enabled_categories: List[str] = field(default_factory=list)
    enabled_codes: Optional[List[str]] = None
    description: str = ""

    def get_effective_codes(self) -> List[str]:
        """Return list of active anomaly codes for this profile."""
        if self.enabled_codes is not None:
            return [c for c in self.enabled_codes if c in TAXONOMY]
        
        if not self.enabled_categories:
            return list(TAXONOMY.keys())
        
        return [
            code for code, defn in TAXONOMY.items()
            if defn.category.value in self.enabled_categories or defn.category.name in self.enabled_categories
        ]


PROFILES: Dict[str, InjectionProfileConfig] = {
    "clean": InjectionProfileConfig(
        name="clean",
        target_rate=0.0,
        default_count_per_anomaly=0,
        enabled_codes=[],
        description="Clean baseline: 0% anomaly rate (zero mutations)",
    ),
    "light": InjectionProfileConfig(
        name="light",
        target_rate=0.01,
        default_count_per_anomaly=1,
        description="Light anomaly profile: ~1% defect rate across all categories",
    ),
    "moderate": InjectionProfileConfig(
        name="moderate",
        target_rate=0.05,
        default_count_per_anomaly=3,
        description="Moderate anomaly profile: ~5% defect rate (standard QA testing baseline)",
    ),
    "heavy": InjectionProfileConfig(
        name="heavy",
        target_rate=0.10,
        default_count_per_anomaly=7,
        description="Heavy anomaly profile: ~10% defect rate for stress-testing QA rules",
    ),
    "targeted": InjectionProfileConfig(
        name="targeted",
        target_rate=0.05,
        default_count_per_anomaly=5,
        description="Targeted anomaly profile: user-selected anomaly codes and counts",
    ),
}


def get_profile(name: str) -> InjectionProfileConfig:
    """Retrieve injection profile configuration by name."""
    clean_name = name.strip().lower()
    if clean_name not in PROFILES:
        raise KeyError(f"Unknown injection profile '{name}'. Available profiles: {list(PROFILES.keys())}")
    return PROFILES[clean_name]

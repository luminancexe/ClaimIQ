"""Configuration parameters and dataset scale profiles for ClaimIQ Generator."""

import os
from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class ScaleProfile:
    name: str
    num_patients: int
    num_providers: int
    num_facilities: int
    num_payers: int
    num_plans: int
    num_encounters: int
    num_claims: int


SCALE_PROFILES: Dict[str, ScaleProfile] = {
    "small": ScaleProfile(
        name="small",
        num_patients=100,
        num_providers=20,
        num_facilities=10,
        num_payers=5,
        num_plans=10,
        num_encounters=500,
        num_claims=1000,
    ),
    "medium": ScaleProfile(
        name="medium",
        num_patients=1000,
        num_providers=100,
        num_facilities=25,
        num_payers=10,
        num_plans=20,
        num_encounters=5000,
        num_claims=10000,
    ),
    "large": ScaleProfile(
        name="large",
        num_patients=10000,
        num_providers=500,
        num_facilities=100,
        num_payers=20,
        num_plans=40,
        num_encounters=50000,
        num_claims=100000,
    ),
}


@dataclass
class GeneratorConfig:
    scale: str = "small"
    seed: int = 42
    batch_size: int = 2500
    start_date: date = date(2025, 1, 1)
    end_date: date = date(2026, 6, 30)
    dry_run: bool = False
    validate: bool = False
    reset: bool = False
    
    # Database connection parameters
    db_host: str = os.getenv("CLAIMIQ_DB_HOST", os.getenv("MYSQL_HOST", "127.0.0.1"))
    db_port: int = int(os.getenv("CLAIMIQ_DB_PORT", os.getenv("MYSQL_PORT", "3306")))
    db_name: str = os.getenv("CLAIMIQ_DB_NAME", os.getenv("MYSQL_DATABASE", "claimiq_test"))
    db_user: str = os.getenv("CLAIMIQ_DB_USER", os.getenv("MYSQL_USER", "root"))
    db_password: str = os.getenv("CLAIMIQ_DB_PASSWORD", os.getenv("MYSQL_PASSWORD", ""))

    @property
    def profile(self) -> ScaleProfile:
        if self.scale.lower() not in SCALE_PROFILES:
            raise ValueError(f"Unknown scale profile '{self.scale}'. Available profiles: {list(SCALE_PROFILES.keys())}")
        return SCALE_PROFILES[self.scale.lower()]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scale": self.scale,
            "seed": self.seed,
            "batch_size": self.batch_size,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "dry_run": self.dry_run,
            "validate": self.validate,
            "reset": self.reset,
            "db_host": self.db_host,
            "db_port": self.db_port,
            "db_name": self.db_name,
            "db_user": self.db_user,
            "profile_targets": {
                "patients": self.profile.num_patients,
                "providers": self.profile.num_providers,
                "facilities": self.profile.num_facilities,
                "payers": self.profile.num_payers,
                "plans": self.profile.num_plans,
                "encounters": self.profile.num_encounters,
                "claims": self.profile.num_claims,
            },
        }

"""Configuration parameters for ClaimIQ Phase 5 QA Rule Engine."""

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


@dataclass
class QAConfig:
    """Execution configuration for QA Rule Engine runs."""
    batch_identifier: str = field(default_factory=lambda: f"BATCH-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}")
    run_reference: Optional[str] = None
    dry_run: bool = False
    rule_filter: Optional[List[str]] = None
    category_filter: Optional[str] = None
    dimension_filter: Optional[str] = None
    create_issues: bool = True
    validate_ground_truth: bool = False

    # Database connection parameters (consistent with GeneratorConfig)
    db_host: str = os.getenv("CLAIMIQ_DB_HOST", os.getenv("MYSQL_HOST", "127.0.0.1"))
    db_port: int = int(os.getenv("CLAIMIQ_DB_PORT", os.getenv("MYSQL_PORT", "3306")))
    db_name: str = os.getenv("CLAIMIQ_DB_NAME", os.getenv("MYSQL_DATABASE", "claimiq_test"))
    db_user: str = os.getenv("CLAIMIQ_DB_USER", os.getenv("MYSQL_USER", "root"))
    db_password: str = os.getenv("CLAIMIQ_DB_PASSWORD", os.getenv("MYSQL_PASSWORD", ""))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_identifier": self.batch_identifier,
            "run_reference": self.run_reference,
            "dry_run": self.dry_run,
            "rule_filter": self.rule_filter,
            "category_filter": self.category_filter,
            "dimension_filter": self.dimension_filter,
            "create_issues": self.create_issues,
            "validate_ground_truth": self.validate_ground_truth,
            "db_host": self.db_host,
            "db_port": self.db_port,
            "db_name": self.db_name,
            "db_user": self.db_user,
        }

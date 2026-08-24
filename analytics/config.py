"""Configuration parameters and filter options for ClaimIQ Analytics Engine."""

import os
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, Any


@dataclass
class AnalyticsConfig:
    """Execution configuration for ClaimIQ Phase 6 Analytics runs."""
    report_type: str = "all"
    batch_identifier: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    provider_filter: Optional[str] = None
    payer_filter: Optional[str] = None
    trend_interval: str = "monthly"  # daily, weekly, monthly
    dry_run: bool = False

    # Database connection parameters (mirroring GeneratorConfig and QAConfig conventions)
    db_host: str = os.getenv("CLAIMIQ_DB_HOST", os.getenv("MYSQL_HOST", "127.0.0.1"))
    db_port: int = int(os.getenv("CLAIMIQ_DB_PORT", os.getenv("MYSQL_PORT", "3306")))
    db_name: str = os.getenv("CLAIMIQ_DB_NAME", os.getenv("MYSQL_DATABASE", "claimiq_test"))
    db_user: str = os.getenv("CLAIMIQ_DB_USER", os.getenv("MYSQL_USER", "root"))
    db_password: str = os.getenv("CLAIMIQ_DB_PASSWORD", os.getenv("MYSQL_PASSWORD", ""))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_type": self.report_type,
            "batch_identifier": self.batch_identifier,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "provider_filter": self.provider_filter,
            "payer_filter": self.payer_filter,
            "trend_interval": self.trend_interval,
            "dry_run": self.dry_run,
            "db_host": self.db_host,
            "db_port": self.db_port,
            "db_name": self.db_name,
            "db_user": self.db_user,
        }

"""Configuration parameters for ClaimIQ Phase 7 Backend & API."""

import os
from dataclasses import dataclass
from typing import Dict, Any


# Development-only fallback secret — production must override via env var
_DEV_JWT_SECRET = "claimiq-dev-secret-DO-NOT-USE-IN-PRODUCTION"


@dataclass
class BackendConfig:
    """Execution configuration for the ClaimIQ FastAPI backend."""

    # Database connection (consistent with GeneratorConfig / AnalyticsConfig)
    db_host: str = os.getenv("CLAIMIQ_DB_HOST", os.getenv("MYSQL_HOST", "127.0.0.1"))
    db_port: int = int(os.getenv("CLAIMIQ_DB_PORT", os.getenv("MYSQL_PORT", "3306")))
    db_name: str = os.getenv("CLAIMIQ_DB_NAME", os.getenv("MYSQL_DATABASE", "claimiq_test"))
    db_user: str = os.getenv("CLAIMIQ_DB_USER", os.getenv("MYSQL_USER", "root"))
    db_password: str = os.getenv("CLAIMIQ_DB_PASSWORD", os.getenv("MYSQL_PASSWORD", ""))

    # JWT
    jwt_secret: str = os.getenv("CLAIMIQ_JWT_SECRET", _DEV_JWT_SECRET)
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = int(os.getenv("CLAIMIQ_JWT_EXPIRATION_MINUTES", "60"))
    jwt_refresh_expiration_minutes: int = int(
        os.getenv("CLAIMIQ_JWT_REFRESH_EXPIRATION_MINUTES", "1440")
    )

    # Server
    api_host: str = os.getenv("CLAIMIQ_API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("CLAIMIQ_API_PORT", "8000"))

    # CORS
    cors_origins: str = os.getenv("CLAIMIQ_CORS_ORIGINS", "*")

    @property
    def is_dev_secret(self) -> bool:
        """Check if the JWT secret is the insecure development fallback."""
        return self.jwt_secret == _DEV_JWT_SECRET

    def to_dict(self) -> Dict[str, Any]:
        return {
            "db_host": self.db_host,
            "db_port": self.db_port,
            "db_name": self.db_name,
            "db_user": self.db_user,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "jwt_algorithm": self.jwt_algorithm,
            "jwt_expiration_minutes": self.jwt_expiration_minutes,
            "jwt_refresh_expiration_minutes": self.jwt_refresh_expiration_minutes,
            "is_dev_secret": self.is_dev_secret,
        }

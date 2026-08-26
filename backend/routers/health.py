"""Health check routes for ClaimIQ Phase 7 Backend API."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends
import pymysql

from backend.schemas.common import HealthResponse
from backend.dependencies import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def root_health_check(conn: Optional[pymysql.Connection] = Depends(get_db)):
    """Liveness and readiness check."""
    db_connected = False
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            db_connected = True
        except Exception:
            db_connected = False

    return HealthResponse(
        status="healthy",
        version="0.7.0",
        database_connected=db_connected,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/api/v1/health", response_model=HealthResponse)
def api_health_check(conn: Optional[pymysql.Connection] = Depends(get_db)):
    """Versioned API health check."""
    return root_health_check(conn)

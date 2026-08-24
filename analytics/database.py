"""Read-only database access layer for ClaimIQ Phase 6 Analytics Engine."""

from typing import Dict, List, Optional, Any, Tuple
import pymysql
from pymysql.cursors import DictCursor
from generator.config import GeneratorConfig
from generator.database import get_connection
from analytics.config import AnalyticsConfig


def get_analytics_connection(config: AnalyticsConfig) -> Optional[pymysql.Connection]:
    """Establish a read-only connection to the ClaimIQ MySQL 8.x database."""
    if config.dry_run:
        # In dry run mode, we may attempt connection, but if offline, return None gracefully
        try:
            gen_cfg = GeneratorConfig(
                db_host=config.db_host,
                db_port=config.db_port,
                db_name=config.db_name,
                db_user=config.db_user,
                db_password=config.db_password,
                dry_run=True,
            )
            conn = get_connection(gen_cfg)
            with conn.cursor() as cur:
                cur.execute("SET SESSION TRANSACTION READ ONLY")
            return conn
        except Exception:
            return None

    gen_cfg = GeneratorConfig(
        db_host=config.db_host,
        db_port=config.db_port,
        db_name=config.db_name,
        db_user=config.db_user,
        db_password=config.db_password,
        dry_run=False,
    )
    conn = get_connection(gen_cfg)
    with conn.cursor() as cur:
        cur.execute("SET SESSION TRANSACTION READ ONLY")
    return conn


def execute_analytical_query(
    conn: pymysql.Connection,
    sql: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> List[Dict[str, Any]]:
    """Execute a parameterized read-only analytical SQL query and return rows as dicts."""
    with conn.cursor(DictCursor) as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()

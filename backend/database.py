"""Read-only database access layer for ClaimIQ Phase 7 Backend API."""

from typing import Optional, List, Dict, Any, Tuple
import pymysql
from pymysql.cursors import DictCursor
from backend.config import BackendConfig


def get_api_connection(config: BackendConfig) -> pymysql.Connection:
    """Establish a read-only connection to the ClaimIQ MySQL 8.x database.

    Every API connection enforces SET SESSION TRANSACTION READ ONLY
    to guarantee the Phase 7 API cannot mutate operational data.
    """
    conn = pymysql.connect(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )
    with conn.cursor() as cur:
        cur.execute("SET SESSION TRANSACTION READ ONLY")
    return conn


def execute_query(
    conn: pymysql.Connection,
    sql: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> List[Dict[str, Any]]:
    """Execute a parameterized read-only SQL query and return rows as dicts."""
    with conn.cursor(DictCursor) as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()


def execute_query_single(
    conn: pymysql.Connection,
    sql: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> Optional[Dict[str, Any]]:
    """Execute a parameterized SQL query and return a single row or None."""
    with conn.cursor(DictCursor) as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()


def execute_count(
    conn: pymysql.Connection,
    sql: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> int:
    """Execute a COUNT query and return the scalar integer result."""
    with conn.cursor(DictCursor) as cur:
        cur.execute(sql, params or ())
        row = cur.fetchone()
        if row:
            # Return the first value regardless of column alias
            return list(row.values())[0]
        return 0

"""Database connection manager, batch insertion engine, and safe reset handler."""

import pymysql
from pymysql.constants import CLIENT
from typing import List, Dict, Tuple, Any, Optional
from generator.config import GeneratorConfig


def get_connection(config: GeneratorConfig) -> pymysql.Connection:
    """Create and return an autocommit-managed PyMySQL connection to MySQL 8.x."""
    conn = pymysql.connect(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        client_flag=CLIENT.MULTI_STATEMENTS,
        autocommit=False,
    )
    return conn


def safe_reset_database(conn: pymysql.Connection) -> Dict[str, int]:
    """Safely delete synthetic transactional and master data in dependency-safe order.

    Preserves reference tables, schema migrations, and QA metadata definitions.
    """
    deletion_order = [
        "reconciliations",
        "denials",
        "adjustments",
        "payments",
        "remittances",
        "claim_status_history",
        "claim_lines",
        "claims",
        "encounter_diagnoses",
        "encounters",
        "patient_coverage",
        "insurance_plans",
        "providers",
        "facilities",
        "payers",
        "patients",
    ]

    deleted_counts: Dict[str, int] = {}
    with conn.cursor() as cursor:
        for table in deletion_order:
            cursor.execute(f"DELETE FROM {table}")
            deleted_counts[table] = cursor.rowcount
            # Reset auto increment counter where appropriate
            try:
                cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
            except Exception:
                pass
        conn.commit()

    return deleted_counts


def bulk_insert(
    conn: pymysql.Connection,
    table: str,
    columns: List[str],
    rows: List[Tuple[Any, ...]],
    batch_size: int = 2500
) -> int:
    """Insert rows in parameterized chunks using executemany."""
    if not rows:
        return 0

    col_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

    total_inserted = 0
    with conn.cursor() as cursor:
        for i in range(0, len(rows), batch_size):
            chunk = rows[i : i + batch_size]
            cursor.executemany(sql, chunk)
            total_inserted += len(chunk)
        conn.commit()

    return total_inserted


def insert_and_fetch_mappings(
    conn: pymysql.Connection,
    table: str,
    columns: List[str],
    rows: List[Tuple[Any, ...]],
    ref_col: str,
    id_col: str,
    batch_size: int = 2500
) -> Dict[str, int]:
    """Bulk insert rows and return an in-memory mapping from business reference to auto-generated database ID."""
    bulk_insert(conn, table, columns, rows, batch_size=batch_size)

    mapping: Dict[str, int] = {}
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT {ref_col}, {id_col} FROM {table}")
        for row in cursor.fetchall():
            mapping[row[ref_col]] = row[id_col]

    return mapping

"""Validation and inspection of static database reference tables."""

import pymysql
from typing import Dict, Any, List

REQUIRED_REFERENCE_COUNTS: Dict[str, int] = {
    "ref_claim_statuses": 7,
    "ref_issue_statuses": 7,
    "ref_severities": 4,
    "ref_dq_dimensions": 7,
    "ref_root_causes": 7,
    "ref_adjustment_group_codes": 5,
    "qa_rule_categories": 7,
}


def verify_reference_data(conn: pymysql.Connection) -> Dict[str, Any]:
    """Verify that all required static reference data is present in the database."""
    status = {"is_valid": True, "counts": {}, "errors": []}

    with conn.cursor() as cursor:
        for table, expected_min in REQUIRED_REFERENCE_COUNTS.items():
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
            row = cursor.fetchone()
            actual = row["cnt"] if isinstance(row, dict) else row[0]
            status["counts"][table] = actual
            if actual < expected_min:
                status["is_valid"] = False
                status["errors"].append(
                    f"Reference table '{table}' has {actual} rows, expected at least {expected_min}."
                )

    return status

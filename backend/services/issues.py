"""Issues service for ClaimIQ Phase 7 Backend API."""

from typing import Optional, Dict, Any, List, Tuple
import pymysql

from backend.database import execute_query, execute_query_single, execute_count


def _serialize_issue_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize an issues table row for summary list."""
    return {
        "issue_id": row["issue_id"],
        "issue_reference": row["issue_reference"],
        "rule_id": row["rule_id"],
        "claim_id": row.get("claim_id"),
        "dimension_code": row["dimension_code"],
        "severity_code": row["severity_code"],
        "current_status_code": row["current_status_code"],
        "detected_at": str(row["detected_at"]),
        "resolved_at": str(row["resolved_at"]) if row.get("resolved_at") else None,
        "variance_amount": str(row["variance_amount"]) if row.get("variance_amount") is not None else None,
    }


def _serialize_issue_detail(row: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize an issue row with rule metadata for detailed view."""
    return {
        "issue_id": row["issue_id"],
        "issue_reference": row["issue_reference"],
        "rule_id": row["rule_id"],
        "rule_code": row.get("rule_code"),
        "rule_name": row.get("rule_name"),
        "claim_id": row.get("claim_id"),
        "dimension_code": row["dimension_code"],
        "severity_code": row["severity_code"],
        "current_status_code": row["current_status_code"],
        "assigned_to_user": row.get("assigned_to_user"),
        "detected_at": str(row["detected_at"]),
        "resolved_at": str(row["resolved_at"]) if row.get("resolved_at") else None,
        "root_cause_code": row.get("root_cause_code"),
        "variance_amount": str(row["variance_amount"]) if row.get("variance_amount") is not None else None,
    }


def get_issues(
    conn: pymysql.Connection,
    page: int = 1,
    page_size: int = 50,
    filters: Optional[Dict[str, Any]] = None,
) -> Tuple[int, List[Dict[str, Any]]]:
    """Retrieve paginated QA defect issues with parameterized filters."""
    where_clauses = ["1=1"]
    params: List[Any] = []
    f = filters or {}

    if f.get("severity"):
        where_clauses.append("severity_code = %s")
        params.append(f["severity"])

    if f.get("dimension"):
        where_clauses.append("dimension_code = %s")
        params.append(f["dimension"])

    if f.get("status"):
        where_clauses.append("current_status_code = %s")
        params.append(f["status"])

    if f.get("rule_id"):
        where_clauses.append("rule_id = %s")
        params.append(int(f["rule_id"]))

    if f.get("claim_id"):
        where_clauses.append("claim_id = %s")
        params.append(int(f["claim_id"]))

    where_sql = " AND ".join(where_clauses)

    count_sql = f"SELECT COUNT(*) as cnt FROM issues WHERE {where_sql}"
    total = execute_count(conn, count_sql, tuple(params))

    offset = (page - 1) * page_size
    query_sql = f"""
        SELECT issue_id, issue_reference, rule_id, claim_id,
               dimension_code, severity_code, current_status_code,
               detected_at, resolved_at, variance_amount
        FROM issues
        WHERE {where_sql}
        ORDER BY issue_id DESC
        LIMIT %s OFFSET %s
    """
    query_params = tuple(params + [page_size, offset])
    rows = execute_query(conn, query_sql, query_params)

    items = [_serialize_issue_summary(r) for r in rows]
    return total, items


def get_issue_by_id(
    conn: pymysql.Connection,
    issue_id: int,
) -> Optional[Dict[str, Any]]:
    """Retrieve detailed information for a single issue including rule metadata."""
    sql = """
        SELECT i.issue_id, i.issue_reference, i.rule_id, r.rule_code, r.rule_name,
               i.claim_id, i.dimension_code, i.severity_code, i.current_status_code,
               i.assigned_to_user, i.detected_at, i.resolved_at, i.root_cause_code,
               i.variance_amount
        FROM issues i
        LEFT JOIN qa_rules r ON i.rule_id = r.rule_id
        WHERE i.issue_id = %s
    """
    row = execute_query_single(conn, sql, (issue_id,))
    if not row:
        return None
    return _serialize_issue_detail(row)

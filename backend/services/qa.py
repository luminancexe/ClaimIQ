"""QA service delegating to existing Phase 5 QA engine, registry, and database."""

from typing import Optional, Dict, Any, List, Tuple
import pymysql

from qa.registry import (
    ALL_RULE_DEFINITIONS,
    get_rule,
    get_rules_by_category,
    get_rules_by_dimension,
    list_all_rules,
)
from qa.scoring import calculate_dq_score, DIMENSION_METADATA
from backend.database import execute_query, execute_query_single, execute_count


def _rule_def_to_dict(r) -> Dict[str, Any]:
    """Convert QARuleDefinition to response dict."""
    return {
        "rule_id": getattr(r, "rule_id", None),
        "rule_code": r.rule_code,
        "category_code": r.category_code,
        "category_id": getattr(r, "category_id", None),
        "dimension_code": r.dimension_code,
        "default_severity_code": r.default_severity_code,
        "rule_name": r.rule_name,
        "description": r.description,
        "detection_method": getattr(r, "detection_method", "SQL_SET"),
        "is_active": r.is_active,
    }


def get_rules(
    conn: Optional[pymysql.Connection] = None,
    category: Optional[str] = None,
    dimension: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve all QA rule definitions, optionally filtered by category or dimension."""
    if category:
        rules = get_rules_by_category(category)
    elif dimension:
        rules = get_rules_by_dimension(dimension)
    else:
        rules = list_all_rules()

    # If DB connection available, augment with DB rule_id
    if conn:
        try:
            db_rules = execute_query(conn, "SELECT rule_id, rule_code FROM qa_rules")
            id_map = {row["rule_code"]: row["rule_id"] for row in db_rules}
            result = []
            for r in rules:
                d = _rule_def_to_dict(r)
                d["rule_id"] = id_map.get(r.rule_code)
                result.append(d)
            return result
        except Exception:
            pass

    return [_rule_def_to_dict(r) for r in rules]


def get_rule_by_id(
    conn: Optional[pymysql.Connection],
    rule_id_or_code: str,
) -> Optional[Dict[str, Any]]:
    """Retrieve a single QA rule by rule_code or integer rule_id."""
    # Try as rule_code or anomaly_code first
    try:
        r = get_rule(rule_id_or_code)
        d = _rule_def_to_dict(r)
        if conn:
            try:
                row = execute_query_single(
                    conn, "SELECT rule_id FROM qa_rules WHERE rule_code = %s", (r.rule_code,)
                )
                if row:
                    d["rule_id"] = row["rule_id"]
            except Exception:
                pass
        return d
    except KeyError:
        pass

    # Try looking up in database by numeric rule_id
    if conn and rule_id_or_code.isdigit():
        try:
            row = execute_query_single(
                conn,
                """SELECT r.rule_id, r.rule_code, c.category_code, r.category_id,
                          r.dimension_code, r.default_severity_code, r.rule_name,
                          r.description, r.is_active
                   FROM qa_rules r
                   LEFT JOIN qa_rule_categories c ON r.category_id = c.category_id
                   WHERE r.rule_id = %s""",
                (int(rule_id_or_code),),
            )
            if row:
                return {
                    "rule_id": row["rule_id"],
                    "rule_code": row["rule_code"],
                    "category_code": row.get("category_code"),
                    "category_id": row.get("category_id"),
                    "dimension_code": row["dimension_code"],
                    "default_severity_code": row["default_severity_code"],
                    "rule_name": row["rule_name"],
                    "description": row["description"],
                    "detection_method": "SQL_SET",
                    "is_active": bool(row["is_active"]),
                }
        except Exception:
            pass

    return None


def get_runs(
    conn: pymysql.Connection,
    page: int = 1,
    page_size: int = 50,
) -> Tuple[int, List[Dict[str, Any]]]:
    """Retrieve paginated QA execution runs from database."""
    total = execute_count(conn, "SELECT COUNT(*) FROM qa_execution_runs")
    offset = (page - 1) * page_size

    sql = """
        SELECT run_id, run_reference, batch_identifier, started_at,
               completed_at, status, total_rules_evaluated,
               total_records_evaluated, total_issues_detected, dq_score
        FROM qa_execution_runs
        ORDER BY run_id DESC
        LIMIT %s OFFSET %s
    """
    rows = execute_query(conn, sql, (page_size, offset))
    items = [
        {
            "run_id": r["run_id"],
            "run_reference": r["run_reference"],
            "batch_identifier": r["batch_identifier"],
            "started_at": str(r["started_at"]),
            "completed_at": str(r["completed_at"]) if r.get("completed_at") else None,
            "status": r["status"],
            "total_rules_evaluated": r["total_rules_evaluated"],
            "total_records_evaluated": r["total_records_evaluated"],
            "total_issues_detected": r["total_issues_detected"],
            "dq_score": str(r["dq_score"]) if r.get("dq_score") is not None else None,
        }
        for r in rows
    ]
    return total, items


def get_run_by_id(
    conn: pymysql.Connection,
    run_id: int,
) -> Optional[Dict[str, Any]]:
    """Retrieve a single QA execution run by run_id."""
    sql = """
        SELECT run_id, run_reference, batch_identifier, started_at,
               completed_at, status, total_rules_evaluated,
               total_records_evaluated, total_issues_detected, dq_score
        FROM qa_execution_runs
        WHERE run_id = %s
    """
    r = execute_query_single(conn, sql, (run_id,))
    if not r:
        return None
    return {
        "run_id": r["run_id"],
        "run_reference": r["run_reference"],
        "batch_identifier": r["batch_identifier"],
        "started_at": str(r["started_at"]),
        "completed_at": str(r["completed_at"]) if r.get("completed_at") else None,
        "status": r["status"],
        "total_rules_evaluated": r["total_rules_evaluated"],
        "total_records_evaluated": r["total_records_evaluated"],
        "total_issues_detected": r["total_issues_detected"],
        "dq_score": str(r["dq_score"]) if r.get("dq_score") is not None else None,
    }


def get_results(
    conn: pymysql.Connection,
    run_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Retrieve per-rule execution telemetry results."""
    where_sql = "WHERE run_id = %s" if run_id else ""
    params = (run_id,) if run_id else ()

    sql = f"""
        SELECT res.result_id, res.run_id, res.rule_id, r.rule_code,
               res.records_evaluated, res.issues_detected,
               res.execution_duration_ms, res.run_status
        FROM qa_results res
        JOIN qa_rules r ON res.rule_id = r.rule_id
        {where_sql}
        ORDER BY res.result_id ASC
    """
    rows = execute_query(conn, sql, params)
    return [
        {
            "result_id": row["result_id"],
            "run_id": row["run_id"],
            "rule_id": row["rule_id"],
            "rule_code": row["rule_code"],
            "records_evaluated": row["records_evaluated"],
            "issues_detected": row["issues_detected"],
            "execution_duration_ms": row["execution_duration_ms"],
            "run_status": row["run_status"],
        }
        for row in rows
    ]


def get_dq_scores(
    conn: pymysql.Connection,
    run_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve or compute 7-dimension Data Quality scores for a run."""
    # Find target run
    target_run_id = run_id
    if target_run_id is None:
        latest = execute_query_single(
            conn, "SELECT run_id FROM qa_execution_runs ORDER BY run_id DESC LIMIT 1"
        )
        if latest:
            target_run_id = latest["run_id"]

    if target_run_id is None:
        # Return default 100.0 if no runs exist
        dim_scores = {
            dim: {
                "dimension_code": dim,
                "dimension_name": meta["name"],
                "weight": meta["weight"],
                "records_evaluated": 0,
                "issues_detected": 0,
                "raw_score": 100.0,
                "weighted_score": round(100.0 * meta["weight"], 2),
            }
            for dim, meta in DIMENSION_METADATA.items()
        }
        return {
            "run_id": None,
            "overall_dq_score": 100.0,
            "total_records_evaluated": 0,
            "total_issues_detected": 0,
            "dimension_scores": dim_scores,
            "severity_breakdown": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
        }

    run_row = get_run_by_id(conn, target_run_id)
    overall_score = float(run_row["dq_score"]) if run_row and run_row.get("dq_score") else 100.0

    # Group issue counts by dimension from issues table for this run context
    dim_issues_sql = """
        SELECT dimension_code, COUNT(*) as cnt
        FROM issues
        GROUP BY dimension_code
    """
    dim_rows = execute_query(conn, dim_issues_sql)
    dim_issue_map = {r["dimension_code"]: r["cnt"] for r in dim_rows}

    # Group severity counts
    sev_sql = """
        SELECT severity_code, COUNT(*) as cnt
        FROM issues
        GROUP BY severity_code
    """
    sev_rows = execute_query(conn, sev_sql)
    sev_map = {r["severity_code"]: r["cnt"] for r in sev_rows}

    dimension_scores = {}
    for dim, meta in DIMENSION_METADATA.items():
        weight = meta["weight"]
        iss_count = dim_issue_map.get(dim, 0)
        raw_score = max(0.0, 100.0 - (iss_count * 5.0))
        dimension_scores[dim] = {
            "dimension_code": dim,
            "dimension_name": meta["name"],
            "weight": weight,
            "records_evaluated": run_row["total_records_evaluated"] if run_row else 0,
            "issues_detected": iss_count,
            "raw_score": round(raw_score, 2),
            "weighted_score": round(raw_score * weight, 2),
        }

    return {
        "run_id": target_run_id,
        "overall_dq_score": round(overall_score, 2),
        "total_records_evaluated": run_row["total_records_evaluated"] if run_row else 0,
        "total_issues_detected": run_row["total_issues_detected"] if run_row else 0,
        "dimension_scores": dimension_scores,
        "severity_breakdown": {
            "Critical": sev_map.get("Critical", 0),
            "High": sev_map.get("High", 0),
            "Medium": sev_map.get("Medium", 0),
            "Low": sev_map.get("Low", 0),
        },
    }

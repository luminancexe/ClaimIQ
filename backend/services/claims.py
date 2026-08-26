"""Claims service for ClaimIQ Phase 7 Backend API."""

from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple
import pymysql

from backend.database import execute_query, execute_query_single, execute_count


def _serialize_claim_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a claims database row preserving Decimal precision as strings."""
    return {
        "claim_id": row["claim_id"],
        "claim_reference": row["claim_reference"],
        "encounter_id": row["encounter_id"],
        "patient_id": row["patient_id"],
        "billing_provider_id": row["billing_provider_id"],
        "payer_id": row["payer_id"],
        "current_status_code": row["current_status_code"],
        "total_billed_amount": str(row["total_billed_amount"]) if row.get("total_billed_amount") is not None else "0.00",
        "submission_date": str(row["submission_date"]) if row.get("submission_date") else "",
        "adjudication_date": str(row["adjudication_date"]) if row.get("adjudication_date") else None,
        "is_reconciled": bool(row["is_reconciled"]),
    }


def _serialize_line_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a claim_lines database row."""
    return {
        "claim_line_id": row["claim_line_id"],
        "claim_id": row["claim_id"],
        "line_number": row["line_number"],
        "cpt_code": row["cpt_code"],
        "procedure_description": row.get("procedure_description"),
        "units": str(row["units"]) if row.get("units") is not None else "1.00",
        "unit_price": str(row["unit_price"]) if row.get("unit_price") is not None else "0.00",
        "line_billed_amount": str(row["line_billed_amount"]) if row.get("line_billed_amount") is not None else "0.00",
        "line_status": row.get("line_status", "Submitted"),
    }


def _serialize_history_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a claim_status_history database row."""
    return {
        "history_id": row["history_id"],
        "claim_id": row["claim_id"],
        "previous_status_code": row.get("previous_status_code"),
        "new_status_code": row["new_status_code"],
        "transition_timestamp": str(row["transition_timestamp"]),
        "transition_reason": row.get("transition_reason"),
        "actor_reference": row.get("actor_reference", "SYSTEM"),
    }


def get_claims(
    conn: pymysql.Connection,
    page: int = 1,
    page_size: int = 50,
    filters: Optional[Dict[str, Any]] = None,
) -> Tuple[int, List[Dict[str, Any]]]:
    """Retrieve paginated claims with parameterized filters."""
    where_clauses = ["1=1"]
    params: List[Any] = []
    f = filters or {}

    if f.get("status"):
        where_clauses.append("current_status_code = %s")
        params.append(f["status"])

    if f.get("claim_reference"):
        where_clauses.append("claim_reference LIKE %s")
        params.append(f"%{f['claim_reference']}%")

    if f.get("payer_id"):
        where_clauses.append("payer_id = %s")
        params.append(int(f["payer_id"]))

    if f.get("provider_id"):
        where_clauses.append("billing_provider_id = %s")
        params.append(int(f["provider_id"]))

    if f.get("patient_id"):
        where_clauses.append("patient_id = %s")
        params.append(int(f["patient_id"]))

    if f.get("start_date"):
        where_clauses.append("submission_date >= %s")
        params.append(f["start_date"])

    if f.get("end_date"):
        where_clauses.append("submission_date <= %s")
        params.append(f["end_date"])

    if f.get("is_reconciled") is not None:
        where_clauses.append("is_reconciled = %s")
        params.append(1 if f["is_reconciled"] else 0)

    where_sql = " AND ".join(where_clauses)

    count_sql = f"SELECT COUNT(*) as cnt FROM claims WHERE {where_sql}"
    total = execute_count(conn, count_sql, tuple(params))

    offset = (page - 1) * page_size
    query_sql = f"""
        SELECT claim_id, claim_reference, encounter_id, patient_id,
               billing_provider_id, payer_id, current_status_code,
               total_billed_amount, submission_date, adjudication_date,
               is_reconciled
        FROM claims
        WHERE {where_sql}
        ORDER BY claim_id ASC
        LIMIT %s OFFSET %s
    """
    query_params = tuple(params + [page_size, offset])
    rows = execute_query(conn, query_sql, query_params)

    items = [_serialize_claim_row(r) for r in rows]
    return total, items


def get_claim_by_id(
    conn: pymysql.Connection,
    claim_id: int,
) -> Optional[Dict[str, Any]]:
    """Retrieve full detail for a single claim, including lines and financial summary."""
    sql = """
        SELECT claim_id, claim_reference, encounter_id, patient_id,
               billing_provider_id, payer_id, current_status_code,
               total_billed_amount, submission_date, adjudication_date,
               is_reconciled
        FROM claims
        WHERE claim_id = %s
    """
    row = execute_query_single(conn, sql, (claim_id,))
    if not row:
        return None

    claim = _serialize_claim_row(row)
    claim["lines"] = get_claim_lines(conn, claim_id)

    # Fetch financial rollup summary
    fin_sql = """
        SELECT
            (SELECT COALESCE(SUM(paid_amount), 0.00) FROM payments WHERE claim_id = %s) as total_paid,
            (SELECT COALESCE(SUM(adjustment_amount), 0.00) FROM adjustments WHERE claim_id = %s) as total_adjusted,
            (SELECT COALESCE(SUM(cl.line_billed_amount), 0.00)
             FROM denials d JOIN claim_lines cl ON d.claim_line_id = cl.claim_line_id
             WHERE d.claim_id = %s) as total_denied
    """
    fin_row = execute_query_single(conn, fin_sql, (claim_id, claim_id, claim_id))
    if fin_row:
        claim["total_paid"] = str(fin_row["total_paid"])
        claim["total_adjusted"] = str(fin_row["total_adjusted"])
        claim["total_denied"] = str(fin_row["total_denied"])
    else:
        claim["total_paid"] = "0.00"
        claim["total_adjusted"] = "0.00"
        claim["total_denied"] = "0.00"

    return claim


def get_claim_lines(
    conn: pymysql.Connection,
    claim_id: int,
) -> List[Dict[str, Any]]:
    """Retrieve line items for a specific claim."""
    sql = """
        SELECT claim_line_id, claim_id, line_number, cpt_code,
               procedure_description, units, unit_price,
               line_billed_amount, line_status
        FROM claim_lines
        WHERE claim_id = %s
        ORDER BY line_number ASC
    """
    rows = execute_query(conn, sql, (claim_id,))
    return [_serialize_line_row(r) for r in rows]


def get_claim_history(
    conn: pymysql.Connection,
    claim_id: int,
) -> List[Dict[str, Any]]:
    """Retrieve lifecycle status transition history for a claim."""
    sql = """
        SELECT history_id, claim_id, previous_status_code,
               new_status_code, transition_timestamp,
               transition_reason, actor_reference
        FROM claim_status_history
        WHERE claim_id = %s
        ORDER BY transition_timestamp ASC, history_id ASC
    """
    rows = execute_query(conn, sql, (claim_id,))
    return [_serialize_history_row(r) for r in rows]

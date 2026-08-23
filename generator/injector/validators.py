"""Phase 4 Anomaly & Ground Truth Validation Suite."""

from typing import Dict, Any, List
import pymysql
from generator.injector.ground_truth import fetch_ground_truth_records, TABLE_PK_MAP


def validate_injected_anomalies(conn: pymysql.Connection) -> Dict[str, Any]:
    """Audit live database to verify that all recorded ground truth mutations exist and are active."""
    results: Dict[str, Any] = {
        "overall_status": "PASS",
        "active_ground_truth_count": 0,
        "verified_mutations": 0,
        "mismatched_mutations": 0,
        "category_counts": {},
        "severity_counts": {},
        "errors": [],
    }

    records = fetch_ground_truth_records(conn, active_only=True)
    results["active_ground_truth_count"] = len(records)

    if not records:
        results["overall_status"] = "CLEAN_BASELINE"
        return results

    with conn.cursor() as cur:
        for rec in records:
            pk_col = TABLE_PK_MAP.get(rec.target_table, "id")
            
            # Count categories and severities
            results["category_counts"][rec.category_name] = results["category_counts"].get(rec.category_name, 0) + 1
            results["severity_counts"][rec.severity_code] = results["severity_counts"].get(rec.severity_code, 0) + 1

            if rec.original_value == "NEW_RECORD":
                # Verify that the newly inserted clone row actually exists
                cur.execute(f"SELECT COUNT(*) AS cnt FROM {rec.target_table} WHERE {pk_col} = %s", (rec.target_record_id,))
                cnt = cur.fetchone()["cnt"]
                if cnt > 0:
                    results["verified_mutations"] += 1
                else:
                    results["mismatched_mutations"] += 1
                    results["errors"].append(f"Ground truth row {rec.target_table}.{rec.target_record_id} not found for {rec.anomaly_code}")
            else:
                # Verify that the column was mutated
                cur.execute(f"SELECT {rec.target_column} AS curr_val FROM {rec.target_table} WHERE {pk_col} = %s", (rec.target_record_id,))
                row = cur.fetchone()
                if row is None:
                    results["mismatched_mutations"] += 1
                    results["errors"].append(f"Target record {rec.target_table}.{rec.target_record_id} missing for {rec.anomaly_code}")
                else:
                    curr_val_str = str(row["curr_val"]) if row["curr_val"] is not None else None
                    # Verify it differs from original or matches mutated
                    if rec.mutated_value is None and curr_val_str is None:
                        results["verified_mutations"] += 1
                    elif curr_val_str == rec.mutated_value or curr_val_str != rec.original_value:
                        results["verified_mutations"] += 1
                    else:
                        results["mismatched_mutations"] += 1
                        results["errors"].append(
                            f"Mutation not observed on {rec.target_table}.{rec.target_column} (ID: {rec.target_record_id}). Expected: {rec.mutated_value}, Found: {curr_val_str}"
                        )

    if results["mismatched_mutations"] > 0:
        results["overall_status"] = "FAIL"

    return results

"""Ground Truth Registry Persistence, JSON Export, and Mutation Reversion."""

import json
import os
from typing import List, Dict, Any, Optional
import pymysql
from generator.injector.models import GroundTruthRecord

TABLE_PK_MAP = {
    "patients": "patient_id",
    "facilities": "facility_id",
    "providers": "provider_id",
    "payers": "payer_id",
    "insurance_plans": "plan_id",
    "patient_coverage": "coverage_id",
    "encounters": "encounter_id",
    "encounter_diagnoses": "diagnosis_id",
    "claims": "claim_id",
    "claim_lines": "claim_line_id",
    "claim_status_history": "history_id",
    "remittances": "remittance_id",
    "payments": "payment_id",
    "adjustments": "adjustment_id",
    "denials": "denial_id",
    "reconciliations": "reconciliation_id",
}


def ensure_ground_truth_table(conn: pymysql.Connection) -> None:
    """Ensure anomaly_ground_truth table exists in the database."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_ground_truth (
                ground_truth_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                anomaly_code VARCHAR(16) NOT NULL,
                category_name VARCHAR(64) NOT NULL,
                severity_code VARCHAR(16) NOT NULL,
                target_table VARCHAR(64) NOT NULL,
                target_record_id BIGINT UNSIGNED NOT NULL,
                target_business_reference VARCHAR(64) NULL,
                target_column VARCHAR(64) NOT NULL,
                original_value TEXT NULL,
                mutated_value TEXT NULL,
                injection_profile VARCHAR(32) NOT NULL,
                injection_seed INT NOT NULL,
                description VARCHAR(255) NOT NULL,
                expected_rule_category VARCHAR(64) NOT NULL,
                injected_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                is_active BOOLEAN NOT NULL DEFAULT 1,
                CONSTRAINT pk_anomaly_ground_truth PRIMARY KEY (ground_truth_id),
                CONSTRAINT fk_agt_severity FOREIGN KEY (severity_code) REFERENCES ref_severities (severity_code) ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """)
        conn.commit()


def save_ground_truth_records(conn: pymysql.Connection, records: List[GroundTruthRecord]) -> int:
    """Batch insert ground truth records into MySQL anomaly_ground_truth table."""
    if not records:
        return 0

    ensure_ground_truth_table(conn)

    sql = """
        INSERT INTO anomaly_ground_truth (
            anomaly_code, category_name, severity_code, target_table,
            target_record_id, target_business_reference, target_column,
            original_value, mutated_value, injection_profile, injection_seed,
            description, expected_rule_category, is_active
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    tuples = [
        (
            r.anomaly_code,
            r.category_name,
            r.severity_code,
            r.target_table,
            r.target_record_id,
            r.target_business_reference,
            r.target_column,
            r.original_value,
            r.mutated_value,
            r.injection_profile,
            r.injection_seed,
            r.description,
            r.expected_rule_category,
            1 if r.is_active else 0,
        )
        for r in records
    ]

    with conn.cursor() as cur:
        cur.executemany(sql, tuples)
        conn.commit()

    return len(records)


def fetch_ground_truth_records(
    conn: pymysql.Connection,
    profile: Optional[str] = None,
    active_only: bool = True
) -> List[GroundTruthRecord]:
    """Fetch stored ground truth records from MySQL."""
    ensure_ground_truth_table(conn)

    query = "SELECT * FROM anomaly_ground_truth WHERE 1=1"
    params: List[Any] = []
    if profile:
        query += " AND injection_profile = %s"
        params.append(profile)
    if active_only:
        query += " AND is_active = 1"
    query += " ORDER BY ground_truth_id ASC"

    with conn.cursor() as cur:
        cur.execute(query, tuple(params))
        rows = cur.fetchall()

    return [
        GroundTruthRecord(
            ground_truth_id=row["ground_truth_id"],
            anomaly_code=row["anomaly_code"],
            category_name=row["category_name"],
            severity_code=row["severity_code"],
            target_table=row["target_table"],
            target_record_id=row["target_record_id"],
            target_business_reference=row.get("target_business_reference"),
            target_column=row["target_column"],
            original_value=row["original_value"],
            mutated_value=row["mutated_value"],
            injection_profile=row["injection_profile"],
            injection_seed=row["injection_seed"],
            description=row["description"],
            expected_rule_category=row["expected_rule_category"],
            injected_at=str(row["injected_at"]) if row.get("injected_at") else None,
            is_active=bool(row["is_active"]),
        )
        for row in rows
    ]


def export_ground_truth_to_json(records: List[GroundTruthRecord], filepath: str) -> str:
    """Export ground truth records list to a formatted JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    payload = {
        "record_count": len(records),
        "anomalies": [r.to_dict() for r in records],
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return filepath


def import_ground_truth_from_json(filepath: str) -> List[GroundTruthRecord]:
    """Load ground truth records from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return [GroundTruthRecord.from_dict(d) for d in payload.get("anomalies", [])]


def revert_ground_truth_mutations(conn: pymysql.Connection) -> Dict[str, int]:
    """Precisely revert all active ground truth mutations and restore clean values."""
    records = fetch_ground_truth_records(conn, active_only=True)
    if not records:
        return {"reverted_count": 0, "deleted_inserted_records": 0}

    reverted_count = 0
    deleted_count = 0

    with conn.cursor() as cur:
        # Revert in reverse order of injection
        for rec in reversed(records):
            pk_col = TABLE_PK_MAP.get(rec.target_table, "id")
            
            if rec.original_value == "NEW_RECORD":
                # Delete newly cloned/inserted anomaly row
                try:
                    cur.execute(f"DELETE FROM {rec.target_table} WHERE {pk_col} = %s", (rec.target_record_id,))
                    deleted_count += 1
                except Exception:
                    pass
            elif rec.original_value is not None and rec.original_value != "NULL" and not rec.original_value.startswith("HAS_LINES_FOR_CLAIM_"):
                # Restore original column value
                try:
                    cur.execute(f"UPDATE {rec.target_table} SET {rec.target_column} = %s WHERE {pk_col} = %s", (rec.original_value, rec.target_record_id))
                    reverted_count += 1
                except Exception:
                    pass
            elif rec.original_value is None or rec.original_value == "NULL":
                # Restore NULL value
                try:
                    cur.execute(f"UPDATE {rec.target_table} SET {rec.target_column} = NULL WHERE {pk_col} = %s", (rec.target_record_id,))
                    reverted_count += 1
                except Exception:
                    pass

        # Mark ground truth records as deactivated
        cur.execute("UPDATE anomaly_ground_truth SET is_active = 0 WHERE is_active = 1")
        conn.commit()

    return {
        "reverted_count": reverted_count,
        "deleted_inserted_records": deleted_count,
        "total_records_processed": len(records),
    }

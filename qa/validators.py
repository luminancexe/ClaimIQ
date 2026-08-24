"""Validation Suite for QA Rule Engine Integrity and Clean Baseline Audits."""

from typing import Dict, Any, List
import pymysql
from qa.models import QARuleDefinition, QADetectionRecord
from qa.registry import list_all_rules, ALL_RULE_DEFINITIONS, RULE_EVALUATOR_MAP


def validate_clean_baseline_qa(conn: pymysql.Connection) -> Dict[str, Any]:
    """Execute all active QA rules against current database to audit clean baseline integrity."""
    rules = list_all_rules()
    all_detections: List[QADetectionRecord] = []
    total_records = 0

    for r in rules:
        evaluator_fn = RULE_EVALUATOR_MAP.get(r.rule_code)
        if evaluator_fn:
            rec_cnt, dets = evaluator_fn(conn, r)
            total_records += rec_cnt
            all_detections.extend(dets)

    return {
        "status": "PASS" if len(all_detections) == 0 else "DEFECTS_DETECTED",
        "rules_evaluated": len(rules),
        "total_records_scanned": total_records,
        "unexpected_finding_count": len(all_detections),
        "findings": [d.to_dict() for d in all_detections[:25]],
    }


def audit_rule_registry_integrity() -> Dict[str, Any]:
    """Audit rule definitions for syntax, dimension codes, and category mappings."""
    errors: List[str] = []
    seen_codes = set()

    for r in ALL_RULE_DEFINITIONS:
        if not r.rule_code:
            errors.append("Rule definition missing rule_code")
        if r.rule_code in seen_codes:
            errors.append(f"Duplicate rule_code '{r.rule_code}' detected")
        seen_codes.add(r.rule_code)

        if not r.sql_logic:
            errors.append(f"Rule '{r.rule_code}' missing sql_logic")
        if not r.anomaly_codes:
            errors.append(f"Rule '{r.rule_code}' missing anomaly_codes mapping")

    return {
        "status": "PASS" if not errors else "FAIL",
        "total_rules": len(ALL_RULE_DEFINITIONS),
        "errors": errors,
    }

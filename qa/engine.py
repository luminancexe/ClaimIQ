"""Core QA Execution Engine for ClaimIQ Phase 5."""

import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import pymysql

from generator.database import get_connection
from generator.config import GeneratorConfig
from qa.config import QAConfig
from qa.models import (
    QARuleDefinition,
    QADetectionRecord,
    QARunTelemetry,
    DQScoreSummary,
    GroundTruthEvaluationResult,
)
from qa.registry import (
    ALL_RULE_DEFINITIONS,
    get_rule,
    get_rules_by_category,
    get_rules_by_dimension,
    RULE_EVALUATOR_MAP,
)
from qa.database import (
    sync_qa_rules_to_database,
    get_db_rule_id_map,
    record_qa_execution_run,
    save_qa_results,
    save_detected_issues,
)
from qa.scoring import calculate_dq_score
from qa.ground_truth import evaluate_ground_truth_accuracy


class QAExecutionEngine:
    """Deterministic QA Rule Engine for SQL Data Quality Analysis."""

    def __init__(self, config: QAConfig):
        self.config = config

    def get_effective_rules(self) -> List[QARuleDefinition]:
        """Resolve active rules filtered by rule code, category, or dimension."""
        rules = list(ALL_RULE_DEFINITIONS)

        if self.config.rule_filter:
            selected_codes = set()
            for c in self.config.rule_filter:
                try:
                    r = get_rule(c)
                    selected_codes.add(r.rule_code)
                except Exception:
                    pass
            rules = [r for r in rules if r.rule_code in selected_codes]

        if self.config.category_filter:
            cat_rules = get_rules_by_category(self.config.category_filter)
            cat_codes = {r.rule_code for r in cat_rules}
            rules = [r for r in rules if r.rule_code in cat_codes]

        if self.config.dimension_filter:
            dim_rules = get_rules_by_dimension(self.config.dimension_filter)
            dim_codes = {r.rule_code for r in dim_rules}
            rules = [r for r in rules if r.rule_code in dim_codes]

        return [r for r in rules if r.is_active]

    def execute(self) -> Dict[str, Any]:
        """Execute the QA engine run, compute DQ scores, and evaluate ground truth."""
        start_dt = datetime.now(timezone.utc)
        start_perf = time.perf_counter()
        rules = self.get_effective_rules()

        run_ref = self.config.run_reference or f"RUN-{start_dt.strftime('%Y%m%d')}-{start_dt.strftime('%H%M%S')}"

        # Setup database connection config
        gen_cfg = GeneratorConfig(
            db_host=self.config.db_host,
            db_port=self.config.db_port,
            db_name=self.config.db_name,
            db_user=self.config.db_user,
            db_password=self.config.db_password,
            dry_run=self.config.dry_run,
        )

        # Handle dry-run simulation mode when DB is unavailable
        conn = None
        use_live_db = True
        try:
            conn = get_connection(gen_cfg)
        except Exception:
            if self.config.dry_run:
                use_live_db = False
            else:
                raise

        telemetry_list: List[QARunTelemetry] = []
        all_detections: List[QADetectionRecord] = []
        gt_result: Optional[GroundTruthEvaluationResult] = None

        if not use_live_db:
            # Standalone simulated dry-run
            for r in rules:
                telemetry_list.append(
                    QARunTelemetry(
                        rule_code=r.rule_code,
                        records_evaluated=100,
                        issues_detected=0,
                        execution_duration_ms=1,
                        run_status="SUCCESS",
                    )
                )
            dq_summary = calculate_dq_score(telemetry_list, all_detections)
            elapsed = time.perf_counter() - start_perf
            return {
                "run_reference": run_ref,
                "batch_identifier": self.config.batch_identifier,
                "status": "DRY_RUN_COMPLETE",
                "rules_evaluated": len(rules),
                "total_records_evaluated": dq_summary.total_records_evaluated,
                "total_issues_detected": 0,
                "overall_dq_score": 100.0,
                "execution_duration_seconds": round(elapsed, 4),
                "dq_summary": dq_summary.to_dict(),
                "detections": [],
                "ground_truth_evaluation": None,
            }

        try:
            rule_id_map = sync_qa_rules_to_database(conn)

            for r in rules:
                evaluator_fn = RULE_EVALUATOR_MAP.get(r.rule_code)
                r_start = time.perf_counter()
                
                if evaluator_fn:
                    records_evaluated, detections = evaluator_fn(conn, r)
                    r_duration_ms = int((time.perf_counter() - r_start) * 1000)
                    all_detections.extend(detections)
                    telemetry_list.append(
                        QARunTelemetry(
                            rule_code=r.rule_code,
                            records_evaluated=records_evaluated,
                            issues_detected=len(detections),
                            execution_duration_ms=r_duration_ms,
                            run_status="SUCCESS",
                        )
                    )
                else:
                    telemetry_list.append(
                        QARunTelemetry(
                            rule_code=r.rule_code,
                            records_evaluated=0,
                            issues_detected=0,
                            execution_duration_ms=0,
                            run_status="SKIPPED",
                        )
                    )

            # Calculate 7-dimension DQ score
            dq_summary = calculate_dq_score(telemetry_list, all_detections)
            completed_dt = datetime.now(timezone.utc)
            elapsed_sec = time.perf_counter() - start_perf

            # Evaluate against ground truth if requested or available
            if self.config.validate_ground_truth or True:
                try:
                    gt_result = evaluate_ground_truth_accuracy(conn=conn, detections=all_detections)
                except Exception:
                    gt_result = None

            # Persist execution run, results, and issues if not dry-run
            run_id = None
            if not self.config.dry_run:
                run_id = record_qa_execution_run(
                    conn=conn,
                    run_reference=run_ref,
                    batch_identifier=self.config.batch_identifier,
                    started_at=start_dt,
                    completed_at=completed_dt,
                    status="COMPLETED",
                    total_rules_evaluated=len(rules),
                    total_records_evaluated=dq_summary.total_records_evaluated,
                    total_issues_detected=len(all_detections),
                    dq_score=dq_summary.overall_dq_score,
                )

                save_qa_results(conn, run_id, telemetry_list, rule_id_map)

                if self.config.create_issues and all_detections:
                    save_detected_issues(conn, all_detections, rule_id_map)

            return {
                "run_id": run_id,
                "run_reference": run_ref,
                "batch_identifier": self.config.batch_identifier,
                "status": "DRY_RUN_COMPLETE" if self.config.dry_run else "COMPLETED",
                "rules_evaluated": len(rules),
                "total_records_evaluated": dq_summary.total_records_evaluated,
                "total_issues_detected": len(all_detections),
                "overall_dq_score": dq_summary.overall_dq_score,
                "execution_duration_seconds": round(elapsed_sec, 4),
                "dq_summary": dq_summary.to_dict(),
                "detections_count": len(all_detections),
                "ground_truth_evaluation": gt_result.to_dict() if gt_result else None,
                "detections": [d.to_dict() for d in all_detections],
            }

        finally:
            if conn:
                conn.close()

"""Anomaly Injection Engine for ClaimIQ Phase 4."""

import os
import time
from typing import List, Dict, Any, Optional
import pymysql

from generator.config import GeneratorConfig
from generator.database import get_connection
from generator.random_state import GeneratorRandomState
from generator.injector.models import GroundTruthRecord, SeverityLevel, AnomalyCategory
from generator.injector.taxonomy import TAXONOMY, get_anomaly_definition
from generator.injector.profiles import get_profile, InjectionProfileConfig
from generator.injector.mutators import MUTATOR_DISPATCH
from generator.injector.ground_truth import (
    ensure_ground_truth_table,
    save_ground_truth_records,
    export_ground_truth_to_json,
)


class AnomalyInjectionEngine:
    """Deterministic, controlled error injection engine for synthetic healthcare claims data."""

    def __init__(
        self,
        config: GeneratorConfig,
        profile_name: str = "moderate",
        seed: Optional[int] = None,
    ):
        self.config = config
        self.profile_name = profile_name.strip().lower()
        self.profile = get_profile(self.profile_name)
        self.seed = seed if seed is not None else config.seed
        self.rng = GeneratorRandomState(self.seed)

    def execute_injection(
        self,
        target_codes: Optional[List[str]] = None,
        override_count: Optional[int] = None,
        export_json: bool = True,
    ) -> Dict[str, Any]:
        """Execute anomaly mutations according to profile or target codes."""
        start_time = time.time()
        active_codes = target_codes if target_codes else self.profile.get_effective_codes()
        active_codes = sorted(active_codes)
        
        if self.profile_name == "clean" or not active_codes:
            return {
                "status": "CLEAN_PROFILE_COMPLETE",
                "profile": self.profile_name,
                "seed": self.seed,
                "anomalies_injected": 0,
                "ground_truth_records": [],
                "elapsed_seconds": time.time() - start_time,
            }

        # If in dry-run mode, check if we can connect to DB; if not, simulate cleanly
        if self.config.dry_run:
            try:
                conn = get_connection(self.config)
                use_live_db = True
            except Exception:
                use_live_db = False
                conn = None

            if not use_live_db:
                # Simulated dry run
                simulated_records: List[GroundTruthRecord] = []
                category_counts: Dict[str, int] = {}
                severity_counts: Dict[str, int] = {s.value: 0 for s in SeverityLevel}

                for code in active_codes:
                    defn = TAXONOMY[code]
                    count = override_count if override_count is not None else self.profile.default_count_per_anomaly
                    for i in range(count):
                        rec = GroundTruthRecord(
                            anomaly_code=code,
                            category_name=defn.category.value,
                            severity_code=defn.severity.value,
                            target_table=defn.target_table,
                            target_record_id=1000 + i,
                            target_business_reference=f"REF-{code}-{i+1}",
                            target_column=defn.target_column,
                            original_value="CLEAN_VAL",
                            mutated_value="MUTATED_VAL",
                            injection_profile=self.profile_name,
                            injection_seed=self.seed,
                            description=defn.description,
                            expected_rule_category=defn.expected_rule_category,
                        )
                        simulated_records.append(rec)
                        category_counts[defn.category.value] = category_counts.get(defn.category.value, 0) + 1
                        severity_counts[defn.severity.value] = severity_counts.get(defn.severity.value, 0) + 1

                elapsed = time.time() - start_time
                return {
                    "status": "DRY_RUN_COMPLETE",
                    "profile": self.profile_name,
                    "seed": self.seed,
                    "anomalies_injected": len(simulated_records),
                    "distinct_anomaly_types": len(active_codes),
                    "category_breakdown": category_counts,
                    "severity_breakdown": severity_counts,
                    "ground_truth_json": None,
                    "elapsed_seconds": elapsed,
                    "ground_truth_records": simulated_records,
                }
        else:
            conn = get_connection(self.config)

        all_records: List[GroundTruthRecord] = []
        category_counts: Dict[str, int] = {}
        severity_counts: Dict[str, int] = {s.value: 0 for s in SeverityLevel}

        try:
            ensure_ground_truth_table(conn)

            for code in active_codes:
                if code not in TAXONOMY:
                    continue

                mutator_fn = MUTATOR_DISPATCH.get(code)
                if not mutator_fn:
                    continue

                count = override_count if override_count is not None else self.profile.default_count_per_anomaly
                if count <= 0:
                    continue

                # Execute mutation
                records = mutator_fn(
                    conn=conn,
                    anomaly_code=code,
                    count=count,
                    rng=self.rng,
                    profile_name=self.profile_name,
                    seed=self.seed,
                    dry_run=self.config.dry_run,
                )

                for rec in records:
                    all_records.append(rec)
                    cat = rec.category_name
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                    sev = rec.severity_code
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1

            if not self.config.dry_run:
                save_ground_truth_records(conn, all_records)
                conn.commit()
            else:
                conn.rollback()

            json_path = None
            if export_json and not self.config.dry_run and all_records:
                json_path = f"reports/ground_truth_{self.profile_name}_{self.seed}.json"
                export_ground_truth_to_json(all_records, json_path)

            elapsed = time.time() - start_time
            return {
                "status": "DRY_RUN_COMPLETE" if self.config.dry_run else "INJECTION_COMPLETE",
                "profile": self.profile_name,
                "seed": self.seed,
                "anomalies_injected": len(all_records),
                "distinct_anomaly_types": len({r.anomaly_code for r in all_records}),
                "category_breakdown": category_counts,
                "severity_breakdown": severity_counts,
                "ground_truth_json": json_path,
                "elapsed_seconds": elapsed,
                "ground_truth_records": all_records,
            }

        except Exception as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Error during anomaly injection: {e}") from e
        finally:
            if conn:
                conn.close()

"""Ground Truth Accuracy Evaluation Engine for ClaimIQ Phase 5."""

from typing import List, Dict, Set, Any, Optional
import pymysql
from generator.injector.models import GroundTruthRecord
from generator.injector.ground_truth import fetch_ground_truth_records
from qa.models import QADetectionRecord, GroundTruthEvaluationResult


def evaluate_ground_truth_accuracy(
    conn: Optional[pymysql.Connection] = None,
    detections: Optional[List[QADetectionRecord]] = None,
    ground_truth_records: Optional[List[GroundTruthRecord]] = None,
) -> GroundTruthEvaluationResult:
    """Compare live QA detection findings against Phase 4 ground truth.

    Matching uses: anomaly_code + target_table + target_record_id (and target_column when needed).
    Calculates: True Positives, False Positives, False Negatives, Precision, Recall, F1 score.
    """
    if detections is None:
        detections = []

    if ground_truth_records is None:
        if conn is None:
            raise ValueError("Either conn or ground_truth_records must be provided.")
        ground_truth_records = fetch_ground_truth_records(conn, active_only=True)

    # Build Ground Truth map
    gt_map: Dict[str, GroundTruthRecord] = {}
    gt_by_cat: Dict[str, List[str]] = {}

    for gt in ground_truth_records:
        key = f"{gt.anomaly_code}|{gt.target_table}|{gt.target_record_id}"
        gt_map[key] = gt
        cat = gt.category_name
        gt_by_cat.setdefault(cat, []).append(key)

    # Build Detections map
    det_map: Dict[str, QADetectionRecord] = {}
    det_by_cat: Dict[str, List[str]] = {}

    for d in detections:
        key = d.get_ground_truth_key()
        det_map[key] = d
        dim = d.dimension_code
        det_by_cat.setdefault(dim, []).append(key)

    gt_keys: Set[str] = set(gt_map.keys())
    det_keys: Set[str] = set(det_map.keys())

    tp_keys = gt_keys & det_keys
    fp_keys = det_keys - gt_keys
    fn_keys = gt_keys - det_keys

    tp = len(tp_keys)
    fp = len(fp_keys)
    fn = len(fn_keys)

    # Precision, Recall, F1 calculation
    if tp + fp > 0:
        precision = tp / (tp + fp)
    else:
        precision = 1.0 if (len(gt_keys) == 0 and len(det_keys) == 0) else 0.0

    if tp + fn > 0:
        recall = tp / (tp + fn)
    else:
        recall = 1.0 if (len(gt_keys) == 0 and len(det_keys) == 0) else 0.0

    if precision + recall > 0:
        f1_score = 2.0 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0

    detection_rate = recall

    # Category breakdown
    category_metrics: Dict[str, Dict[str, Any]] = {}
    for cat, keys in gt_by_cat.items():
        c_gt = set(keys)
        c_tp = len(c_gt & det_keys)
        c_fn = len(c_gt - det_keys)
        c_rec = (c_tp / (c_tp + c_fn)) if (c_tp + c_fn) > 0 else 1.0
        category_metrics[cat] = {
            "ground_truth_count": len(c_gt),
            "true_positives": c_tp,
            "false_negatives": c_fn,
            "recall": round(c_rec, 4),
        }

    unmatched_gt = [gt_map[k].to_dict() for k in fn_keys]
    unmatched_det = [det_map[k].to_dict() for k in fp_keys]

    return GroundTruthEvaluationResult(
        total_ground_truth_anomalies=len(gt_keys),
        total_qa_detections=len(det_keys),
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        detection_rate=detection_rate,
        category_metrics=category_metrics,
        unmatched_ground_truth=unmatched_gt,
        unmatched_detections=unmatched_det,
    )

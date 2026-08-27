export interface QARule {
  rule_id?: number | null;
  rule_code: string;
  category_code?: string | null;
  category_id?: number | null;
  dimension_code: string;
  default_severity_code: string;
  rule_name: string;
  description: string;
  detection_method?: string | null;
  is_active: boolean;
}

export interface QARun {
  run_id: number;
  run_reference: string;
  batch_identifier: string;
  started_at: string;
  completed_at?: string | null;
  status: string;
  total_rules_evaluated: number;
  total_records_evaluated: number;
  total_issues_detected: number;
  dq_score?: string | null;
}

export interface QAResult {
  result_id: number;
  run_id: number;
  rule_id: number;
  rule_code?: string | null;
  records_evaluated: number;
  issues_detected: number;
  execution_duration_ms: number;
  run_status: string;
}

export interface DQDimensionScore {
  dimension_code: string;
  dimension_name: string;
  weight: number;
  records_evaluated: number;
  issues_detected: number;
  raw_score: number;
  weighted_score: number;
}

export interface DQScoreSummary {
  run_id?: number | null;
  overall_dq_score: number;
  total_records_evaluated: number;
  total_issues_detected: number;
  dimension_scores: Record<string, DQDimensionScore>;
  severity_breakdown: Record<string, number>;
}

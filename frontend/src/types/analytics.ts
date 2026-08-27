export interface FinancialOverview {
  total_billed: string;
  total_paid: string;
  total_contractual_adjustments: string;
  total_patient_responsibility: string;
  total_variance: string;
  unreconciled_amount: string;
  overpayment_exposure: string;
  underpayment_exposure: string;
  total_denied_amount: string;
  reconciliation_rate: number;
  payment_rate: number;
  financial_integrity_rate: number;
}

export interface ClaimsKPIs {
  total_claims: number;
  status_distribution: Record<string, number>;
  adjudicated_claims: number;
  adjudication_rate: number;
  reconciled_claims: number;
}

export interface PaymentKPIs {
  total_payments_count: number;
  total_paid_amount: string;
  average_payment_amount: string;
  zero_payment_count: number;
  average_payment_turnaround_days?: number | null;
}

export interface DenialKPIs {
  total_denials: number;
  denial_rate: number;
  appealable_rate: number;
  top_denial_reasons: Array<{
    reason_code?: string;
    count?: number;
    description?: string;
    [key: string]: unknown;
  }>;
  denial_financial_exposure: string;
}

export interface QAKPIs {
  total_issues: number;
  issues_by_severity: Record<string, number>;
  issues_by_dimension: Record<string, number>;
  average_dq_score: number;
  clean_record_rate: number;
  defect_density: number;
}

export interface KPIOverview {
  claims: ClaimsKPIs;
  payments: PaymentKPIs;
  denials: DenialKPIs;
  qa: QAKPIs;
}

export interface DQTrendPoint {
  time_bucket: string;
  overall_dq_score: number;
  dimension_scores: Record<string, number>;
  issue_count: number;
  claim_volume: number;
}

export interface DQTrendsSummary {
  interval: string;
  points: DQTrendPoint[];
  rolling_average_score: number;
  score_velocity: number;
  trend_direction: string;
}

export interface RootCauseItem {
  anomaly_category: string;
  anomaly_code: string;
  rule_code: string;
  description: string;
  severity_code: string;
  dimension_code: string;
  issue_count: number;
  percentage_of_total: number;
  cumulative_percentage: number;
  financial_exposure: string;
}

export interface RootCauseResponse {
  items: RootCauseItem[];
  pareto_cutoff_index: number;
  primary_defect_driver: string;
  total_issues_analyzed: number;
}

export interface RecurrencePattern {
  entity_type: string;
  entity_identifier: string;
  anomaly_code: string;
  occurrence_count: number;
  first_detected_at?: string | null;
  last_detected_at?: string | null;
  recurrence_rank: number;
}

export interface RecurrenceResponse {
  recurring_cluster_count: number;
  top_repeat_entities: RecurrencePattern[];
  repeat_issue_rate: number;
  total_repeating_occurrences: number;
}

export interface ProviderScorecard {
  provider_id: number;
  provider_reference: string;
  provider_name: string;
  specialty: string;
  facility_id?: number | null;
  facility_name?: string | null;
  claim_volume: number;
  total_billed: string;
  total_paid: string;
  payment_rate: number;
  denial_rate: number;
  issue_count: number;
  issue_density: number;
  dq_score: number;
  financial_exposure: string;
}

export interface PayerScorecard {
  payer_id: number;
  payer_reference: string;
  payer_name: string;
  payer_type: string;
  claim_volume: number;
  total_billed: string;
  total_paid: string;
  denial_rate: number;
  payment_rate: number;
  average_adjudication_latency_days: number;
  average_payment_latency_days: number;
  timely_filing_compliance_rate: number;
  contractual_adjustment_ratio: number;
  issue_count: number;
}

export interface AnalyticsOverview {
  financial?: FinancialOverview | null;
  kpis?: KPIOverview | null;
  root_cause?: RootCauseResponse | null;
}

export interface ProviderDetail {
  provider_id: number;
  provider_reference: string;
  facility_id?: number | null;
  first_name: string;
  last_name: string;
  npi: string;
  taxonomy_code: string;
  specialty: string;
}

export interface PayerDetail {
  payer_id: number;
  payer_reference: string;
  payer_name: string;
  payer_type: string;
  timely_filing_days: number;
}

export interface IssueSummary {
  issue_id: number;
  issue_reference: string;
  rule_id: number;
  claim_id?: number | null;
  dimension_code: string;
  severity_code: string;
  current_status_code: string;
  detected_at: string;
  resolved_at?: string | null;
  variance_amount?: string | null;
}

export interface IssueDetail {
  issue_id: number;
  issue_reference: string;
  rule_id: number;
  rule_code?: string | null;
  rule_name?: string | null;
  claim_id?: number | null;
  dimension_code: string;
  severity_code: string;
  current_status_code: string;
  assigned_to_user?: string | null;
  detected_at: string;
  resolved_at?: string | null;
  root_cause_code?: string | null;
  variance_amount?: string | null;
}

export interface IssueFilters {
  severity?: string;
  dimension?: string;
  status?: string;
  rule_id?: number;
  claim_id?: number;
  page?: number;
  page_size?: number;
}

export interface ProviderFilters {
  specialty?: string;
  page?: number;
  page_size?: number;
}

export interface PayerFilters {
  payer_type?: string;
  page?: number;
  page_size?: number;
}

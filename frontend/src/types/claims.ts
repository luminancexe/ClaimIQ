export interface ClaimSummary {
  claim_id: number;
  claim_reference: string;
  encounter_id: number;
  patient_id: number;
  billing_provider_id: number;
  payer_id: number;
  current_status_code: string;
  total_billed_amount: string;
  submission_date: string;
  adjudication_date: string | null;
  is_reconciled: boolean;
}

export interface ClaimLine {
  claim_line_id: number;
  claim_id: number;
  line_number: number;
  cpt_code: string;
  procedure_description?: string | null;
  units: string;
  unit_price: string;
  line_billed_amount: string;
  line_status: string;
}

export interface StatusHistoryEntry {
  history_id: number;
  claim_id: number;
  previous_status_code?: string | null;
  new_status_code: string;
  transition_timestamp: string;
  transition_reason?: string | null;
  actor_reference: string;
}

export interface ClaimDetail extends ClaimSummary {
  lines?: ClaimLine[];
  total_paid?: string;
  total_adjusted?: string;
  total_denied?: string;
}

export interface ClaimFilters {
  status?: string;
  claim_reference?: string;
  payer_id?: number;
  provider_id?: number;
  patient_id?: number;
  start_date?: string;
  end_date?: string;
  is_reconciled?: boolean;
  page?: number;
  page_size?: number;
}

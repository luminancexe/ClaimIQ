import { apiClient } from './client';
import { PayerDetail, PayerScorecard, PayerFilters, PaginatedResponse } from '../types';

export async function getPayers(params?: PayerFilters): Promise<PaginatedResponse<PayerDetail>> {
  return apiClient<PaginatedResponse<PayerDetail>>('/payers', {
    params: params as Record<string, string | number | boolean | undefined | null>,
  });
}

export async function getPayerById(payerId: number | string): Promise<PayerDetail> {
  return apiClient<PayerDetail>(`/payers/${payerId}`);
}

export async function getPayerScorecard(payerId: number | string): Promise<PayerScorecard> {
  return apiClient<PayerScorecard>(`/payers/${payerId}/scorecard`);
}

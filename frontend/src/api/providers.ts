import { apiClient } from './client';
import { ProviderDetail, ProviderScorecard, ProviderFilters, PaginatedResponse } from '../types';

export async function getProviders(params?: ProviderFilters): Promise<PaginatedResponse<ProviderDetail>> {
  return apiClient<PaginatedResponse<ProviderDetail>>('/providers', {
    params: params as Record<string, string | number | boolean | undefined | null>,
  });
}

export async function getProviderById(providerId: number | string): Promise<ProviderDetail> {
  return apiClient<ProviderDetail>(`/providers/${providerId}`);
}

export async function getProviderScorecard(providerId: number | string): Promise<ProviderScorecard> {
  return apiClient<ProviderScorecard>(`/providers/${providerId}/scorecard`);
}

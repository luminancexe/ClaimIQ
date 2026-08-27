import { apiClient } from './client';
import { ClaimSummary, ClaimDetail, ClaimLine, StatusHistoryEntry, ClaimFilters, PaginatedResponse } from '../types';

export async function getClaims(filters?: ClaimFilters): Promise<PaginatedResponse<ClaimSummary>> {
  return apiClient<PaginatedResponse<ClaimSummary>>('/claims', {
    params: filters as Record<string, string | number | boolean | undefined | null>,
  });
}

export async function getClaimById(claimId: number | string): Promise<ClaimDetail> {
  return apiClient<ClaimDetail>(`/claims/${claimId}`);
}

export async function getClaimLines(claimId: number | string): Promise<ClaimLine[]> {
  return apiClient<ClaimLine[]>(`/claims/${claimId}/lines`);
}

export async function getClaimHistory(claimId: number | string): Promise<StatusHistoryEntry[]> {
  return apiClient<StatusHistoryEntry[]>(`/claims/${claimId}/history`);
}

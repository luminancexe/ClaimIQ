import { apiClient } from './client';
import { IssueSummary, IssueDetail, IssueFilters, PaginatedResponse } from '../types';

export async function getIssues(params?: IssueFilters): Promise<PaginatedResponse<IssueSummary>> {
  return apiClient<PaginatedResponse<IssueSummary>>('/issues', {
    params: params as Record<string, string | number | boolean | undefined | null>,
  });
}

export async function getIssueById(issueId: number | string): Promise<IssueDetail> {
  return apiClient<IssueDetail>(`/issues/${issueId}`);
}

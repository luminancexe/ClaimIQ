import { apiClient } from './client';
import { QARule, QARun, QAResult, DQScoreSummary, IssueSummary, IssueFilters, PaginatedResponse } from '../types';

export async function getQARules(params?: { category?: string; dimension?: string }): Promise<QARule[]> {
  return apiClient<QARule[]>('/qa/rules', { params });
}

export async function getQARuleById(ruleId: string | number): Promise<QARule> {
  return apiClient<QARule>(`/qa/rules/${ruleId}`);
}

export async function getQARuns(params?: { page?: number; page_size?: number }): Promise<PaginatedResponse<QARun>> {
  return apiClient<PaginatedResponse<QARun>>('/qa/runs', { params });
}

export async function getQARunById(runId: number | string): Promise<QARun> {
  return apiClient<QARun>(`/qa/runs/${runId}`);
}

export async function getQAResults(runId?: number): Promise<QAResult[]> {
  return apiClient<QAResult[]>('/qa/results', { params: runId ? { run_id: runId } : undefined });
}

export async function getDQScores(runId?: number): Promise<DQScoreSummary> {
  return apiClient<DQScoreSummary>('/qa/scores', { params: runId ? { run_id: runId } : undefined });
}

export async function getQAIssues(filters?: IssueFilters): Promise<PaginatedResponse<IssueSummary>> {
  return apiClient<PaginatedResponse<IssueSummary>>('/qa/issues', {
    params: filters as Record<string, string | number | boolean | undefined | null>,
  });
}

import { apiClient } from './client';
import {
  AnalyticsOverview,
  FinancialOverview,
  KPIOverview,
  ProviderScorecard,
  PayerScorecard,
  DQTrendsSummary,
  RootCauseResponse,
  RecurrenceResponse,
} from '../types';

export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  return apiClient<AnalyticsOverview>('/analytics/overview');
}

export async function getFinancialAnalytics(): Promise<FinancialOverview> {
  return apiClient<FinancialOverview>('/analytics/financial');
}

export async function getKPIAnalytics(): Promise<KPIOverview> {
  return apiClient<KPIOverview>('/analytics/kpis');
}

export async function getProviderAnalytics(): Promise<ProviderScorecard[]> {
  return apiClient<ProviderScorecard[]>('/analytics/providers');
}

export async function getProviderScorecardById(providerId: number | string): Promise<ProviderScorecard> {
  return apiClient<ProviderScorecard>(`/analytics/providers/${providerId}`);
}

export async function getPayerAnalytics(): Promise<PayerScorecard[]> {
  return apiClient<PayerScorecard[]>('/analytics/payers');
}

export async function getPayerScorecardById(payerId: number | string): Promise<PayerScorecard> {
  return apiClient<PayerScorecard>(`/analytics/payers/${payerId}`);
}

export async function getTrends(interval: 'daily' | 'weekly' | 'monthly' = 'monthly'): Promise<DQTrendsSummary> {
  return apiClient<DQTrendsSummary>('/analytics/trends', { params: { interval } });
}

export async function getRootCauses(): Promise<RootCauseResponse> {
  return apiClient<RootCauseResponse>('/analytics/root-causes');
}

export async function getRecurrence(): Promise<RecurrenceResponse> {
  return apiClient<RecurrenceResponse>('/analytics/recurrence');
}

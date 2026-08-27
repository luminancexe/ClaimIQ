import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { FinancialPage } from '../features/analytics/FinancialPage';
import { TrendsPage } from '../features/analytics/TrendsPage';
import { RootCausesPage } from '../features/analytics/RootCausesPage';
import { RecurrencePage } from '../features/analytics/RecurrencePage';
import * as analyticsApi from '../api/analytics';


describe('Analytics Suite Views', () => {
  it('renders FinancialPage with reconciliation and exposure metrics', async () => {
    vi.spyOn(analyticsApi, 'getFinancialAnalytics').mockResolvedValue({
      total_billed: '2500000.00',
      total_paid: '1750000.00',
      total_contractual_adjustments: '500000.00',
      total_patient_responsibility: '100000.00',
      total_variance: '150000.00',
      unreconciled_amount: '25000.00',
      overpayment_exposure: '80000.00',
      underpayment_exposure: '70000.00',
      total_denied_amount: '200000.00',
      reconciliation_rate: 0.95,
      payment_rate: 0.70,
      financial_integrity_rate: 0.94,
    });

    render(
      <MemoryRouter>
        <FinancialPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('$2,500,000.00')).toBeInTheDocument();
    expect(screen.getByText('Reconciliation Rate')).toBeInTheDocument();
    expect(screen.getByText('95.0%')).toBeInTheDocument();
  });

  it('renders TrendsPage and handles interval switching', async () => {
    const getTrendsSpy = vi.spyOn(analyticsApi, 'getTrends').mockResolvedValue({
      interval: 'monthly',
      points: [
        {
          time_bucket: '2026-03',
          overall_dq_score: 95.0,
          dimension_scores: {},
          issue_count: 50,
          claim_volume: 5000,
        },
      ],
      rolling_average_score: 95.0,
      score_velocity: 1.5,
      trend_direction: 'IMPROVING',
    });

    render(
      <MemoryRouter>
        <TrendsPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('Longitudinal Quality Trends')).toBeInTheDocument();
    expect(screen.getByText('IMPROVING')).toBeInTheDocument();

    const weeklyBtn = screen.getByText('weekly');
    await act(async () => {
      fireEvent.click(weeklyBtn);
    });
    expect(getTrendsSpy).toHaveBeenCalledWith('weekly');
  });

  it('renders RootCausesPage with Pareto defect rankings', async () => {
    vi.spyOn(analyticsApi, 'getRootCauses').mockResolvedValue({
      items: [
        {
          anomaly_category: 'FINANCIAL',
          anomaly_code: 'E001',
          rule_code: 'R-E001',
          description: 'Duplicate header amount',
          severity_code: 'Critical',
          dimension_code: 'Financial',
          issue_count: 100,
          percentage_of_total: 50.0,
          cumulative_percentage: 50.0,
          financial_exposure: '50000.00',
        },
      ],
      pareto_cutoff_index: 2,
      primary_defect_driver: 'E001',
      total_issues_analyzed: 200,
    });

    render(
      <MemoryRouter>
        <RootCausesPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('Pareto 80/20 Root Cause Analysis')).toBeInTheDocument();
    expect(screen.getAllByText('E001').length).toBeGreaterThan(0);
    expect(screen.getByText('Top 2 Anomalies')).toBeInTheDocument();
  });

  it('renders RecurrencePage with repeat offender clusters', async () => {
    vi.spyOn(analyticsApi, 'getRecurrence').mockResolvedValue({
      recurring_cluster_count: 5,
      top_repeat_entities: [
        {
          entity_type: 'PROVIDER',
          entity_identifier: 'PRV-0010',
          anomaly_code: 'E005',
          occurrence_count: 12,
          first_detected_at: '2026-02-01T00:00:00Z',
          last_detected_at: '2026-03-01T00:00:00Z',
          recurrence_rank: 1,
        },
      ],
      repeat_issue_rate: 0.22,
      total_repeating_occurrences: 45,
    });

    render(
      <MemoryRouter>
        <RecurrencePage />
      </MemoryRouter>
    );

    expect(await screen.findByText('Recurrence & Repeat Offender Clusters')).toBeInTheDocument();
    expect(screen.getByText('PRV-0010')).toBeInTheDocument();
    expect(screen.getByText('#1')).toBeInTheDocument();
  });
});

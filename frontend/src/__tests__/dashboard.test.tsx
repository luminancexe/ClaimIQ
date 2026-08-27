import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { MemoryRouter } from 'react-router-dom';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import * as analyticsApi from '../api/analytics';
import * as qaApi from '../api/qa';

describe('DashboardPage', () => {
  it('renders all 8 KPI cards and overview charts when API succeeds', async () => {
    vi.spyOn(analyticsApi, 'getAnalyticsOverview').mockResolvedValue({
      financial: {
        total_billed: '5000000.00',
        total_paid: '3500000.00',
        total_contractual_adjustments: '1000000.00',
        total_patient_responsibility: '200000.00',
        total_variance: '300000.00',
        unreconciled_amount: '50000.00',
        overpayment_exposure: '150000.00',
        underpayment_exposure: '100000.00',
        total_denied_amount: '400000.00',
        reconciliation_rate: 0.945,
        payment_rate: 0.70,
        financial_integrity_rate: 0.96,
      },
      kpis: {
        claims: {
          total_claims: 12500,
          status_distribution: { Paid: 9000, Denied: 1500, Pending: 2000 },
          adjudicated_claims: 10500,
          adjudication_rate: 0.84,
          reconciled_claims: 9900,
        },
        payments: {
          total_payments_count: 9000,
          total_paid_amount: '3500000.00',
          average_payment_amount: '388.88',
          zero_payment_count: 120,
          average_payment_turnaround_days: 14.2,
        },
        denials: {
          total_denials: 1500,
          denial_rate: 0.12,
          appealable_rate: 0.65,
          top_denial_reasons: [{ reason_code: 'CO-16', count: 450 }],
          denial_financial_exposure: '400000.00',
        },
        qa: {
          total_issues: 320,
          issues_by_severity: { Critical: 45, High: 85, Medium: 120, Low: 70 },
          issues_by_dimension: { Financial: 110, Referential: 80 },
          average_dq_score: 91.8,
          clean_record_rate: 0.974,
          defect_density: 0.025,
        },
      },
      root_cause: {
        items: [
          {
            anomaly_category: 'FINANCIAL',
            anomaly_code: 'E001',
            rule_code: 'R-E001',
            description: 'Duplicate claim line amount',
            severity_code: 'Critical',
            dimension_code: 'Financial',
            issue_count: 85,
            percentage_of_total: 26.5,
            cumulative_percentage: 26.5,
            financial_exposure: '125000.00',
          },
        ],
        pareto_cutoff_index: 3,
        primary_defect_driver: 'E001',
        total_issues_analyzed: 320,
      },
    });

    vi.spyOn(analyticsApi, 'getTrends').mockResolvedValue({
      interval: 'monthly',
      points: [
        {
          time_bucket: '2026-01',
          overall_dq_score: 89.5,
          dimension_scores: { Financial: 90.0 },
          issue_count: 120,
          claim_volume: 4000,
        },
        {
          time_bucket: '2026-02',
          overall_dq_score: 91.8,
          dimension_scores: { Financial: 92.5 },
          issue_count: 100,
          claim_volume: 4200,
        },
      ],
      rolling_average_score: 90.6,
      score_velocity: 2.3,
      trend_direction: 'IMPROVING',
    });

    vi.spyOn(qaApi, 'getDQScores').mockResolvedValue({
      overall_dq_score: 91.8,
      total_records_evaluated: 12500,
      total_issues_detected: 320,
      dimension_scores: {
        Financial: {
          dimension_code: 'Financial',
          dimension_name: 'Financial Integrity',
          weight: 0.25,
          records_evaluated: 12500,
          issues_detected: 110,
          raw_score: 91.2,
          weighted_score: 22.8,
        },
      },
      severity_breakdown: { Critical: 45, High: 85, Medium: 120, Low: 70 },
    });

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    // Verify 8 KPI metric cards exist
    expect(await screen.findByText('Total Claims')).toBeInTheDocument();
    expect(screen.getByText('12,500')).toBeInTheDocument();
    expect(screen.getByText('Total Billed')).toBeInTheDocument();
    expect(screen.getByText('$5,000,000.00')).toBeInTheDocument();
    expect(screen.getByText('Denial Rate')).toBeInTheDocument();
    expect(screen.getByText('12.0%')).toBeInTheDocument();
    expect(screen.getByText('Overall DQ Score')).toBeInTheDocument();
    expect(screen.getByText('91.8/100')).toBeInTheDocument();
    expect(screen.getByText('Total QA Issues')).toBeInTheDocument();
    expect(screen.getByText('320')).toBeInTheDocument();
    expect(screen.getByText('Clean Record Rate')).toBeInTheDocument();
    expect(screen.getByText('97.4%')).toBeInTheDocument();
    expect(screen.getByText('Reconciliation Rate')).toBeInTheDocument();
    expect(screen.getByText('94.5%')).toBeInTheDocument();
  });
});

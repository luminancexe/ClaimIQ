import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QARulesPage } from '../features/qa/QARulesPage';
import { QARunsPage } from '../features/qa/QARunsPage';
import { DQScoresPage } from '../features/qa/DQScoresPage';
import * as qaApi from '../api/qa';


describe('QA Observatory Views', () => {
  it('renders QARulesPage with rule catalog', async () => {
    vi.spyOn(qaApi, 'getQARules').mockResolvedValue([
      {
        rule_id: 1,
        rule_code: 'R-E001',
        category_code: 'FINANCIAL',
        dimension_code: 'Financial',
        default_severity_code: 'Critical',
        rule_name: 'Line Amount Matches Header',
        description: 'Verifies sum of line items equals header total billed',
        is_active: true,
      },
    ]);

    render(
      <MemoryRouter>
        <QARulesPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('R-E001')).toBeInTheDocument();
    expect(screen.getByText('Line Amount Matches Header')).toBeInTheDocument();
  });

  it('renders QARunsPage with execution run batch', async () => {
    vi.spyOn(qaApi, 'getQARuns').mockResolvedValue({
      page: 1,
      page_size: 25,
      total: 1,
      total_pages: 1,
      has_next: false,
      has_previous: false,
      items: [
        {
          run_id: 50,
          run_reference: 'RUN-2026-050',
          batch_identifier: 'BATCH-SYNTH-01',
          started_at: '2026-03-01T00:00:00Z',
          completed_at: '2026-03-01T00:02:00Z',
          status: 'COMPLETED',
          total_rules_evaluated: 67,
          total_records_evaluated: 10000,
          total_issues_detected: 150,
          dq_score: '93.5',
        },
      ],
    });

    render(
      <MemoryRouter>
        <QARunsPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('RUN-2026-050')).toBeInTheDocument();
    expect(screen.getByText('BATCH-SYNTH-01')).toBeInTheDocument();
    expect(screen.getByText('93.5/100')).toBeInTheDocument();
  });

  it('renders DQScoresPage with 7-dimension scorecard breakdown', async () => {
    vi.spyOn(qaApi, 'getDQScores').mockResolvedValue({
      overall_dq_score: 93.5,
      total_records_evaluated: 10000,
      total_issues_detected: 150,
      dimension_scores: {
        Referential: {
          dimension_code: 'Referential',
          dimension_name: 'Referential Integrity',
          weight: 0.15,
          records_evaluated: 10000,
          issues_detected: 10,
          raw_score: 98.0,
          weighted_score: 14.7,
        },
      },
      severity_breakdown: { Critical: 20, High: 40, Medium: 60, Low: 30 },
    });

    render(
      <MemoryRouter>
        <DQScoresPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('93.5')).toBeInTheDocument();
    expect(screen.getByText('Referential Integrity')).toBeInTheDocument();
    expect(screen.getByText('14.70 pts')).toBeInTheDocument();
  });
});

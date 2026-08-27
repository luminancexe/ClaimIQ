import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { IssuesListPage } from '../features/issues/IssuesListPage';
import { IssueDetailPage } from '../features/issues/IssueDetailPage';
import * as issuesApi from '../api/issues';

describe('Issues Explorer (Read-Only)', () => {
  it('renders IssuesListPage with observational defect list', async () => {
    vi.spyOn(issuesApi, 'getIssues').mockResolvedValue({
      page: 1,
      page_size: 50,
      total: 1,
      total_pages: 1,
      has_next: false,
      has_previous: false,
      items: [
        {
          issue_id: 88,
          issue_reference: 'ISS-2026-00088',
          rule_id: 12,
          claim_id: 405,
          dimension_code: 'Financial',
          severity_code: 'Critical',
          current_status_code: 'OPEN',
          detected_at: '2026-03-02T12:00:00Z',
          variance_amount: '350.00',
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={['/issues']}>
        <IssuesListPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('ISS-2026-00088')).toBeInTheDocument();
    expect(screen.getByText('RULE-#12')).toBeInTheDocument();
    expect(screen.getByText('$350.00')).toBeInTheDocument();
    expect(screen.getByText('OBSERVATIONAL VIEW ONLY')).toBeInTheDocument();
  });

  it('renders IssueDetailPage in strictly read-only mode with zero mutation controls', async () => {
    vi.spyOn(issuesApi, 'getIssueById').mockResolvedValue({
      issue_id: 88,
      issue_reference: 'ISS-2026-00088',
      rule_id: 12,
      rule_code: 'R-E012',
      rule_name: 'Payment Exceeds Allowed Amount',
      claim_id: 405,
      dimension_code: 'Financial',
      severity_code: 'Critical',
      current_status_code: 'OPEN',
      assigned_to_user: null,
      detected_at: '2026-03-02T12:00:00Z',
      root_cause_code: 'E012',
      variance_amount: '350.00',
    });

    render(
      <MemoryRouter initialEntries={['/issues/88']}>
        <Routes>
          <Route path="/issues/:id" element={<IssueDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('ISS-2026-00088')).toBeInTheDocument();
    expect(screen.getByText('R-E012')).toBeInTheDocument();
    expect(screen.getByText('Observational Telemetry Mode')).toBeInTheDocument();

    // Verify STRICT Phase 8 Boundaries: Prohibited mutation buttons must NOT exist
    expect(screen.queryByRole('button', { name: /assign/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /resolve/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /dismiss/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /triage/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /remediate/i })).not.toBeInTheDocument();
  });
});

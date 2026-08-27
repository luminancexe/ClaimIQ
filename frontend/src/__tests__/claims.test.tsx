import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ClaimsExplorerPage } from '../features/claims/ClaimsExplorerPage';
import { ClaimDetailPage } from '../features/claims/ClaimDetailPage';
import * as claimsApi from '../api/claims';

describe('Claims Explorer & Detail Views', () => {
  it('renders ClaimsExplorerPage with paginated claims list', async () => {
    vi.spyOn(claimsApi, 'getClaims').mockResolvedValue({
      page: 1,
      page_size: 50,
      total: 100,
      total_pages: 2,
      has_next: true,
      has_previous: false,
      items: [
        {
          claim_id: 101,
          claim_reference: 'CLM-2026-00101',
          encounter_id: 501,
          patient_id: 1001,
          billing_provider_id: 201,
          payer_id: 301,
          current_status_code: 'Paid',
          total_billed_amount: '1250.00',
          submission_date: '2026-03-01T00:00:00Z',
          adjudication_date: '2026-03-05T00:00:00Z',
          is_reconciled: true,
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={['/claims']}>
        <ClaimsExplorerPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('CLM-2026-00101')).toBeInTheDocument();
    expect(screen.getByText('PT-001001')).toBeInTheDocument();
    expect(screen.getByText('PRV-0201')).toBeInTheDocument();
    expect(screen.getByText('PAY-301')).toBeInTheDocument();
    expect(screen.getByText('$1,250.00')).toBeInTheDocument();
  });

  it('renders ClaimDetailPage with itemized procedure lines and history', async () => {
    vi.spyOn(claimsApi, 'getClaimById').mockResolvedValue({
      claim_id: 101,
      claim_reference: 'CLM-2026-00101',
      encounter_id: 501,
      patient_id: 1001,
      billing_provider_id: 201,
      payer_id: 301,
      current_status_code: 'Paid',
      total_billed_amount: '1250.00',
      submission_date: '2026-03-01T00:00:00Z',
      adjudication_date: '2026-03-05T00:00:00Z',
      is_reconciled: true,
      total_paid: '1100.00',
      total_adjusted: '150.00',
      total_denied: '0.00',
    });

    vi.spyOn(claimsApi, 'getClaimLines').mockResolvedValue([
      {
        claim_line_id: 901,
        claim_id: 101,
        line_number: 1,
        cpt_code: '99213',
        procedure_description: 'Office Visit Level 3',
        units: '1.00',
        unit_price: '1250.00',
        line_billed_amount: '1250.00',
        line_status: 'Paid',
      },
    ]);

    vi.spyOn(claimsApi, 'getClaimHistory').mockResolvedValue([
      {
        history_id: 1,
        claim_id: 101,
        previous_status_code: 'Submitted',
        new_status_code: 'Paid',
        transition_timestamp: '2026-03-05T10:00:00Z',
        transition_reason: 'Adjudication Complete',
        actor_reference: 'PAYER_AUTO_ADJUDICATOR',
      },
    ]);

    render(
      <MemoryRouter initialEntries={['/claims/101']}>
        <Routes>
          <Route path="/claims/:id" element={<ClaimDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('CLM-2026-00101')).toBeInTheDocument();
    expect(screen.getByText('99213')).toBeInTheDocument();
    expect(screen.getByText('Office Visit Level 3')).toBeInTheDocument();
    expect(screen.getByText('PAYER_AUTO_ADJUDICATOR')).toBeInTheDocument();
  });
});

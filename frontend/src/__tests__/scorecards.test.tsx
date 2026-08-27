import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ProvidersListPage } from '../features/providers/ProvidersListPage';
import { ProviderDetailPage } from '../features/providers/ProviderDetailPage';
import { PayersListPage } from '../features/payers/PayersListPage';
import { PayerDetailPage } from '../features/payers/PayerDetailPage';
import * as analyticsApi from '../api/analytics';
import * as providersApi from '../api/providers';
import * as payersApi from '../api/payers';

describe('Provider & Payer Scorecard Views', () => {
  it('renders ProvidersListPage and ProviderDetailPage', async () => {
    vi.spyOn(analyticsApi, 'getProviderAnalytics').mockResolvedValue([
      {
        provider_id: 10,
        provider_reference: 'PRV-0010',
        provider_name: 'Dr. Evelyn Carter',
        specialty: 'Cardiology',
        claim_volume: 350,
        total_billed: '450000.00',
        total_paid: '315000.00',
        payment_rate: 0.70,
        denial_rate: 0.08,
        issue_count: 12,
        issue_density: 0.034,
        dq_score: 94.5,
        financial_exposure: '15000.00',
      },
    ]);

    vi.spyOn(providersApi, 'getProviderById').mockResolvedValue({
      provider_id: 10,
      provider_reference: 'PRV-0010',
      first_name: 'Evelyn',
      last_name: 'Carter',
      npi: '1234567890',
      taxonomy_code: '207RC0000X',
      specialty: 'Cardiology',
    });

    vi.spyOn(providersApi, 'getProviderScorecard').mockResolvedValue({
      provider_id: 10,
      provider_reference: 'PRV-0010',
      provider_name: 'Dr. Evelyn Carter',
      specialty: 'Cardiology',
      claim_volume: 350,
      total_billed: '450000.00',
      total_paid: '315000.00',
      payment_rate: 0.70,
      denial_rate: 0.08,
      issue_count: 12,
      issue_density: 0.034,
      dq_score: 94.5,
      financial_exposure: '15000.00',
    });

    const { unmount } = render(
      <MemoryRouter initialEntries={['/providers']}>
        <ProvidersListPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('PRV-0010')).toBeInTheDocument();
    expect(screen.getByText('Dr. Evelyn Carter')).toBeInTheDocument();
    unmount();

    render(
      <MemoryRouter initialEntries={['/providers/10']}>
        <Routes>
          <Route path="/providers/:id" element={<ProviderDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('Evelyn Carter')).toBeInTheDocument();
    expect(screen.getByText('1234567890')).toBeInTheDocument();
  });

  it('renders PayersListPage and PayerDetailPage', async () => {
    vi.spyOn(analyticsApi, 'getPayerAnalytics').mockResolvedValue([
      {
        payer_id: 5,
        payer_reference: 'PAY-005',
        payer_name: 'BlueCross Anthem',
        payer_type: 'Commercial',
        claim_volume: 2400,
        total_billed: '3000000.00',
        total_paid: '2100000.00',
        denial_rate: 0.10,
        payment_rate: 0.70,
        average_adjudication_latency_days: 12.5,
        average_payment_latency_days: 15.2,
        timely_filing_compliance_rate: 0.99,
        contractual_adjustment_ratio: 0.20,
        issue_count: 65,
      },
    ]);

    vi.spyOn(payersApi, 'getPayerById').mockResolvedValue({
      payer_id: 5,
      payer_reference: 'PAY-005',
      payer_name: 'BlueCross Anthem',
      payer_type: 'Commercial',
      timely_filing_days: 90,
    });

    vi.spyOn(payersApi, 'getPayerScorecard').mockResolvedValue({
      payer_id: 5,
      payer_reference: 'PAY-005',
      payer_name: 'BlueCross Anthem',
      payer_type: 'Commercial',
      claim_volume: 2400,
      total_billed: '3000000.00',
      total_paid: '2100000.00',
      denial_rate: 0.10,
      payment_rate: 0.70,
      average_adjudication_latency_days: 12.5,
      average_payment_latency_days: 15.2,
      timely_filing_compliance_rate: 0.99,
      contractual_adjustment_ratio: 0.20,
      issue_count: 65,
    });

    const { unmount } = render(
      <MemoryRouter initialEntries={['/payers']}>
        <PayersListPage />
      </MemoryRouter>
    );

    expect(await screen.findByText('PAY-005')).toBeInTheDocument();
    expect(screen.getByText('BlueCross Anthem')).toBeInTheDocument();
    unmount();

    render(
      <MemoryRouter initialEntries={['/payers/5']}>
        <Routes>
          <Route path="/payers/:id" element={<PayerDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText('BlueCross Anthem')).toBeInTheDocument();
    expect(screen.getAllByText(/90 Days/).length).toBeGreaterThan(0);
  });
});

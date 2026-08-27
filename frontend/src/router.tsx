import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './context/AuthContext';
import { AppShell } from './components/layout/AppShell';

import { LoginPage } from './features/auth/LoginPage';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { ClaimsExplorerPage } from './features/claims/ClaimsExplorerPage';
import { ClaimDetailPage } from './features/claims/ClaimDetailPage';
import { QAOverviewPage } from './features/qa/QAOverviewPage';
import { QARulesPage } from './features/qa/QARulesPage';
import { QARunsPage } from './features/qa/QARunsPage';
import { QARunDetailPage } from './features/qa/QARunDetailPage';
import { DQScoresPage } from './features/qa/DQScoresPage';
import { AnalyticsHubPage } from './features/analytics/AnalyticsHubPage';
import { FinancialPage } from './features/analytics/FinancialPage';
import { KPIsPage } from './features/analytics/KPIsPage';
import { TrendsPage } from './features/analytics/TrendsPage';
import { RootCausesPage } from './features/analytics/RootCausesPage';
import { RecurrencePage } from './features/analytics/RecurrencePage';
import { ProvidersListPage } from './features/providers/ProvidersListPage';
import { ProviderDetailPage } from './features/providers/ProviderDetailPage';
import { PayersListPage } from './features/payers/PayersListPage';
import { PayerDetailPage } from './features/payers/PayerDetailPage';
import { IssuesListPage } from './features/issues/IssuesListPage';
import { IssueDetailPage } from './features/issues/IssueDetailPage';

const LayoutWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ProtectedRoute>
    <AppShell>{children}</AppShell>
  </ProtectedRoute>
);

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Root redirect to /dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Dashboard */}
      <Route
        path="/dashboard"
        element={
          <LayoutWrapper>
            <DashboardPage />
          </LayoutWrapper>
        }
      />

      {/* Claims Explorer */}
      <Route
        path="/claims"
        element={
          <LayoutWrapper>
            <ClaimsExplorerPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/claims/:id"
        element={
          <LayoutWrapper>
            <ClaimDetailPage />
          </LayoutWrapper>
        }
      />

      {/* QA Observatory */}
      <Route
        path="/qa"
        element={
          <LayoutWrapper>
            <QAOverviewPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/qa/rules"
        element={
          <LayoutWrapper>
            <QARulesPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/qa/runs"
        element={
          <LayoutWrapper>
            <QARunsPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/qa/runs/:id"
        element={
          <LayoutWrapper>
            <QARunDetailPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/qa/scores"
        element={
          <LayoutWrapper>
            <DQScoresPage />
          </LayoutWrapper>
        }
      />

      {/* Analytics Suite */}
      <Route
        path="/analytics"
        element={
          <LayoutWrapper>
            <AnalyticsHubPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/analytics/financial"
        element={
          <LayoutWrapper>
            <FinancialPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/analytics/kpis"
        element={
          <LayoutWrapper>
            <KPIsPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/analytics/trends"
        element={
          <LayoutWrapper>
            <TrendsPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/analytics/root-causes"
        element={
          <LayoutWrapper>
            <RootCausesPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/analytics/recurrence"
        element={
          <LayoutWrapper>
            <RecurrencePage />
          </LayoutWrapper>
        }
      />

      {/* Providers */}
      <Route
        path="/providers"
        element={
          <LayoutWrapper>
            <ProvidersListPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/providers/:id"
        element={
          <LayoutWrapper>
            <ProviderDetailPage />
          </LayoutWrapper>
        }
      />

      {/* Payers */}
      <Route
        path="/payers"
        element={
          <LayoutWrapper>
            <PayersListPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/payers/:id"
        element={
          <LayoutWrapper>
            <PayerDetailPage />
          </LayoutWrapper>
        }
      />

      {/* Issues Explorer */}
      <Route
        path="/issues"
        element={
          <LayoutWrapper>
            <IssuesListPage />
          </LayoutWrapper>
        }
      />
      <Route
        path="/issues/:id"
        element={
          <LayoutWrapper>
            <IssueDetailPage />
          </LayoutWrapper>
        }
      />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

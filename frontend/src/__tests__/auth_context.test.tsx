import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth, ProtectedRoute } from '../context/AuthContext';
import * as authApi from '../api/auth';

const TestAuthConsumer: React.FC = () => {
  const { user, isAuthenticated, login, logout, hasRole } = useAuth();
  return (
    <div>
      <div data-testid="auth-status">{isAuthenticated ? 'LOGGED_IN' : 'LOGGED_OUT'}</div>
      <div data-testid="user-name">{user?.username || 'NONE'}</div>
      <div data-testid="user-role">{user?.role || 'NONE'}</div>
      <div data-testid="is-admin">{hasRole('ADMIN') ? 'YES' : 'NO'}</div>
      <div data-testid="is-qa">{hasRole('QA_REVIEWER') ? 'YES' : 'NO'}</div>
      <button onClick={() => login({ username: 'analyst', password: 'Analyst@123' })}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext & ProtectedRoute', () => {
  it('handles login and role checking properly', async () => {
    vi.spyOn(authApi, 'login').mockResolvedValue({
      access_token: 'acc-token-123',
      refresh_token: 'ref-token-123',
      token_type: 'bearer',
      expires_in: 3600,
    });

    vi.spyOn(authApi, 'getMe').mockResolvedValue({
      user_id: 'USR-002',
      username: 'analyst',
      role: 'ANALYST',
    });

    render(
      <MemoryRouter>
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByTestId('auth-status').textContent).toBe('LOGGED_OUT');

    await act(async () => {
      screen.getByText('Login').click();
    });

    expect(screen.getByTestId('auth-status').textContent).toBe('LOGGED_IN');
    expect(screen.getByTestId('user-name').textContent).toBe('analyst');
    expect(screen.getByTestId('user-role').textContent).toBe('ANALYST');
    expect(screen.getByTestId('is-admin').textContent).toBe('NO');
  });

  it('renders restricted role access warning for prohibited roles', async () => {
    vi.spyOn(authApi, 'getMe').mockResolvedValue({
      user_id: 'USR-004',
      username: 'viewer',
      role: 'VIEWER',
    });
    localStorage.setItem('claimiq_access_token', 'mock-viewer-token');

    render(
      <MemoryRouter initialEntries={['/admin-only']}>
        <AuthProvider>
          <Routes>
            <Route
              path="/admin-only"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <div>Admin Secret Area</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    // Wait for async profile fetch
    const restrictedHeader = await screen.findByText('Access Restricted');
    expect(restrictedHeader).toBeInTheDocument();
    expect(screen.queryByText('Admin Secret Area')).not.toBeInTheDocument();
  });
});

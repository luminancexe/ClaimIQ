import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  apiClient,
  ApiError,
  setStoredTokens,
  getStoredAccessToken,
  clearStoredTokens,
} from '../api/client';

describe('API Client', () => {
  beforeEach(() => {
    clearStoredTokens();
    vi.restoreAllMocks();
  });

  it('attaches Authorization header when access token is present', async () => {
    setStoredTokens('test-access-token', 'test-refresh-token');

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ status: 'healthy', version: '0.7.0' }),
      headers: new Headers(),
    });
    global.fetch = mockFetch;

    const res = await apiClient<{ status: string }>('/health');
    expect(res.status).toBe('healthy');
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/health'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-access-token',
        }),
      })
    );
  });

  it('throws ApiError with sanitized message on backend error', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: async () => ({
        error_code: 'CLAIM_NOT_FOUND',
        message: 'Claim 9999 not found in dataset',
        request_id: 'req-12345',
      }),
      headers: new Headers({ 'X-Request-ID': 'req-12345' }),
    });
    global.fetch = mockFetch;

    await expect(apiClient('/claims/9999')).rejects.toThrow(ApiError);
    try {
      await apiClient('/claims/9999');
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      expect(apiErr.status).toBe(404);
      expect(apiErr.errorCode).toBe('CLAIM_NOT_FOUND');
      expect(apiErr.message).toBe('Claim 9999 not found in dataset');
      expect(apiErr.requestId).toBe('req-12345');
    }
  });

  it('performs automatic token refresh and retry on 401 Unauthorized', async () => {
    setStoredTokens('expired-access-token', 'valid-refresh-token');

    let meCallCount = 0;
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes('/auth/refresh')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            access_token: 'new-refreshed-token',
            refresh_token: 'new-refresh-token-2',
            token_type: 'bearer',
            expires_in: 3600,
          }),
          headers: new Headers(),
        });
      }
      if (url.includes('/auth/me')) {
        meCallCount++;
        if (meCallCount === 1) {
          // First attempt: 401
          return Promise.resolve({
            ok: false,
            status: 401,
            statusText: 'Unauthorized',
            json: async () => ({ error_code: 'UNAUTHORIZED', message: 'Token expired' }),
            headers: new Headers(),
          });
        }
        // Second attempt: 200 with new token
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({ user_id: 'USR-001', username: 'admin', role: 'ADMIN' }),
          headers: new Headers(),
        });
      }
      return Promise.reject(new Error('Unknown url'));
    });
    global.fetch = mockFetch;

    const res = await apiClient<{ username: string }>('/auth/me');
    expect(res.username).toBe('admin');
    expect(getStoredAccessToken()).toBe('new-refreshed-token');
    expect(meCallCount).toBe(2);
  });
});

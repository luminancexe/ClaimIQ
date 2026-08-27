import { ErrorResponse, TokenResponse } from '../types';

export class ApiError extends Error {
  status: number;
  errorCode: string;
  requestId?: string;

  constructor(status: number, errorCode: string, message: string, requestId?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errorCode = errorCode;
    this.requestId = requestId;
  }
}

const ACCESS_TOKEN_KEY = 'claimiq_access_token';
const REFRESH_TOKEN_KEY = 'claimiq_refresh_token';

let refreshPromise: Promise<string> | null = null;

export function getStoredAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getStoredRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setStoredTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearStoredTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export const API_BASE_URL = (
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) ||
  'http://localhost:8000/api/v1'
).replace(/\/$/, '');

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>;
  skipAuth?: boolean;
}

async function requestTokenRefresh(): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const refreshToken = getStoredRefreshToken();
      if (!refreshToken) {
        clearStoredTokens();
        window.dispatchEvent(new CustomEvent('claimiq:auth:expired'));
        throw new ApiError(401, 'UNAUTHORIZED', 'No refresh token available. Please log in again.');
      }

      try {
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (!refreshRes.ok) {
          clearStoredTokens();
          window.dispatchEvent(new CustomEvent('claimiq:auth:expired'));
          throw new ApiError(401, 'UNAUTHORIZED', 'Session expired. Please log in again.');
        }

        const data: TokenResponse = await refreshRes.json();
        setStoredTokens(data.access_token, data.refresh_token);
        return data.access_token;
      } catch (err) {
        clearStoredTokens();
        window.dispatchEvent(new CustomEvent('claimiq:auth:expired'));
        throw err;
      } finally {
        refreshPromise = null;
      }
    })();
  }
  return refreshPromise;
}

export async function apiClient<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, skipAuth = false, headers = {}, ...restOptions } = options;

  let url = endpoint.startsWith('http')
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        searchParams.append(key, String(val));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString;
    }
  }

  const reqHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(headers as Record<string, string>),
  };

  if (!skipAuth) {
    const token = getStoredAccessToken();
    if (token) {
      reqHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...restOptions,
      headers: reqHeaders,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Network request failed';
    throw new ApiError(0, 'NETWORK_ERROR', `Unable to connect to ClaimIQ server: ${message}`);
  }

  // Handle 401 Unauthorized with token refresh & retry
  if (
    response.status === 401 &&
    !skipAuth &&
    !endpoint.includes('/auth/login') &&
    !endpoint.includes('/auth/refresh')
  ) {
    const newToken = await requestTokenRefresh();
    reqHeaders['Authorization'] = `Bearer ${newToken}`;

    const retryRes = await fetch(url, {
      ...restOptions,
      headers: reqHeaders,
    });

    if (!retryRes.ok) {
      let errorData: ErrorResponse;
      try {
        errorData = await retryRes.json();
      } catch {
        errorData = {
          error_code: `HTTP_${retryRes.status}`,
          message: retryRes.statusText || 'An unexpected error occurred',
        };
      }
      const reqId = retryRes.headers.get('X-Request-ID') || errorData.request_id;
      throw new ApiError(
        retryRes.status,
        errorData.error_code || 'HTTP_ERROR',
        errorData.message || 'Request failed',
        reqId
      );
    }
    return retryRes.json();
  }

  if (!response.ok) {
    let errorData: ErrorResponse;
    try {
      errorData = await response.json();
    } catch {
      errorData = {
        error_code: `HTTP_${response.status}`,
        message: response.statusText || 'An unexpected error occurred',
      };
    }
    const reqId = response.headers.get('X-Request-ID') || errorData.request_id;
    throw new ApiError(
      response.status,
      errorData.error_code || 'HTTP_ERROR',
      errorData.message || 'Request failed',
      reqId
    );
  }

  return response.json();
}

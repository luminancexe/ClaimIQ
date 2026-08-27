import { apiClient } from './client';
import { LoginRequest, TokenResponse, RefreshRequest, UserProfile } from '../types';

export async function login(request: LoginRequest): Promise<TokenResponse> {
  return apiClient<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(request),
    skipAuth: true,
  });
}

export async function refreshToken(request: RefreshRequest): Promise<TokenResponse> {
  return apiClient<TokenResponse>('/auth/refresh', {
    method: 'POST',
    body: JSON.stringify(request),
    skipAuth: true,
  });
}

export async function getMe(): Promise<UserProfile> {
  return apiClient<UserProfile>('/auth/me');
}

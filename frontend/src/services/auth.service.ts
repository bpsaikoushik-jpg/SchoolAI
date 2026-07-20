import api from './api';
import type { AuthUser, LoginPayload, TokenResponse } from '../types/auth';

// Backend expects OAuth2PasswordRequestForm: x-www-form-urlencoded
// with `username` (the user's email) and `password`.
export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.set('username', payload.email);
  form.set('password', payload.password);

  const { data } = await api.post<TokenResponse>('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return data;
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const { data } = await api.get<AuthUser>('/users/me');
  return data;
}

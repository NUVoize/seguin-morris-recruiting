/**
 * Auth API methods + session user shape.
 */

import {apiRequest} from './client';

export interface AuthUser {
  id: string;
  full_name: string;
  email: string;
  preferred_language: string;
  role_name: string | null;
  permissions: Record<string, boolean>;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  user: AuthUser;
}

export const auth = {
  login(email: string, password: string): Promise<TokenResponse> {
    return apiRequest<TokenResponse>('/auth/login', {
      method: 'POST',
      body: {email, password}
    });
  },

  me(token?: string | null): Promise<AuthUser> {
    return apiRequest<AuthUser>('/auth/me', {token});
  },

  logout(): Promise<void> {
    return apiRequest<void>('/auth/logout', {method: 'POST'});
  }
};

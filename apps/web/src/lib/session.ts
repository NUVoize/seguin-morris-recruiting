/**
 * Client-side session helpers. The JWT lives in a `sm_session` cookie so both
 * the browser (Authorization header on API calls) and the Next.js server
 * (SSR fetches, route protection in proxy.ts) can read it.
 *
 * v1 trade-off, documented: the cookie is intentionally NOT httpOnly because
 * the SPA calls the FastAPI origin directly with a Bearer header. Acceptable
 * for an internal tool; revisit with a BFF proxy if exposure widens.
 */

export const SESSION_COOKIE = 'sm_session';
const MAX_AGE_SECONDS = 12 * 60 * 60; // mirrors the 12h JWT expiry

export function getSessionToken(): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${SESSION_COOKIE}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export function setSessionToken(token: string): void {
  document.cookie = `${SESSION_COOKIE}=${encodeURIComponent(token)}; path=/; max-age=${MAX_AGE_SECONDS}; SameSite=Lax; Secure`;
}

export function clearSessionToken(): void {
  document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0; SameSite=Lax; Secure`;
}

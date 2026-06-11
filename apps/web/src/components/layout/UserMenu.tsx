'use client';

import {useEffect, useState} from 'react';
import {useLocale, useTranslations} from 'next-intl';

import {auth, type AuthUser} from '@/lib/api';
import {clearSessionToken, getSessionToken} from '@/lib/session';

/**
 * Signed-in identity chip + sign-out. Fetches /auth/me once when a session
 * cookie is present; renders nothing when signed out (public landing).
 */
export function UserMenu() {
  const t = useTranslations('shell');
  const locale = useLocale();
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    if (!getSessionToken()) return;
    let cancelled = false;
    auth
      .me()
      .then((u) => {
        if (!cancelled) setUser(u);
      })
      .catch(() => {
        /* 401 handling lives in the API client */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!user) return null;

  async function handleSignOut() {
    try {
      await auth.logout();
    } catch {
      /* stateless JWT — clearing the cookie is what matters */
    }
    clearSessionToken();
    window.location.assign(`/${locale}/login`);
  }

  const firstName = user.full_name.split(' ')[0];

  return (
    <div className="flex items-center gap-2.5">
      <span className="hidden items-center gap-2 sm:flex">
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-navy font-display text-xs font-bold uppercase text-white">
          {firstName.charAt(0)}
        </span>
        <span className="text-sm font-medium text-steel-700">{firstName}</span>
        {user.role_name && (
          <span className="rounded bg-steel-50 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wide text-steel-500 ring-1 ring-steel-100">
            {user.role_name}
          </span>
        )}
      </span>
      <button
        type="button"
        onClick={handleSignOut}
        className="rounded-md px-2 py-1 text-xs font-medium text-steel-400 transition hover:bg-steel-50 hover:text-steel-700"
      >
        {t('sign_out')}
      </button>
    </div>
  );
}

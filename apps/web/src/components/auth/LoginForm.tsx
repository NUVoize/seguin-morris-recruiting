'use client';

import {useState} from 'react';
import {useRouter, useSearchParams} from 'next/navigation';
import {useLocale, useTranslations} from 'next-intl';

import {ApiError, auth} from '@/lib/api';
import {setSessionToken} from '@/lib/session';

/**
 * Email/password form. On success: store the JWT in the session cookie and
 * hard-navigate to the requested page (hard nav so proxy.ts and server
 * components see the new cookie immediately).
 */
export function LoginForm() {
  const t = useTranslations('login');
  const locale = useLocale();
  const searchParams = useSearchParams();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    if (!email || !password || busy) return;
    setBusy(true);
    setError(null);
    try {
      const resp = await auth.login(email.trim(), password);
      setSessionToken(resp.access_token);
      const next = searchParams.get('next');
      const safeNext = next && next.startsWith('/') && !next.startsWith('//') ? next : '/run';
      window.location.assign(`/${locale}${safeNext}`);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 401
          ? t('error_invalid')
          : t('error_generic')
      );
      setBusy(false);
    }
  }

  return (
    <div className="mt-7 space-y-4">
      {error && (
        <p className="rounded-md border border-danger/30 bg-danger-soft px-3 py-2 text-sm text-danger">
          {error}
        </p>
      )}

      <div>
        <label
          htmlFor="login-email"
          className="font-mono text-[10px] font-medium uppercase tracking-[0.2em] text-steel-400"
        >
          {t('email_label')}
        </label>
        <input
          id="login-email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          className="mt-1.5 w-full rounded-lg border border-steel-200 bg-white px-3 py-2.5 text-sm text-steel-900 transition focus:border-navy focus:outline-none focus:ring-1 focus:ring-navy"
          placeholder={t('email_placeholder')}
        />
      </div>

      <div>
        <label
          htmlFor="login-password"
          className="font-mono text-[10px] font-medium uppercase tracking-[0.2em] text-steel-400"
        >
          {t('password_label')}
        </label>
        <input
          id="login-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          className="mt-1.5 w-full rounded-lg border border-steel-200 bg-white px-3 py-2.5 text-sm text-steel-900 transition focus:border-navy focus:outline-none focus:ring-1 focus:ring-navy"
          placeholder="••••••••"
        />
      </div>

      <button
        type="button"
        onClick={handleSubmit}
        disabled={busy || !email || !password}
        className="w-full rounded-lg bg-ember px-4 py-3 font-display text-base font-semibold uppercase tracking-wide text-white shadow-lg shadow-ember/20 transition hover:bg-ember-600 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {busy ? t('signing_in') : t('sign_in')}
      </button>

      <p className="pt-2 text-center text-[11px] text-steel-400">{t('internal_note')}</p>
    </div>
  );
}

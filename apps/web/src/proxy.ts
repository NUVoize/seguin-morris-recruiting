import createMiddleware from 'next-intl/middleware';
import {NextRequest, NextResponse} from 'next/server';
import {routing} from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

const SESSION_COOKIE = 'sm_session';

// Auth kill-switch, mirrors the API's AUTH_ENABLED. When off (dev default),
// no route is gated and /login still works if visited directly. Set
// NEXT_PUBLIC_AUTH_ENABLED=true to re-arm (always set it in production).
const AUTH_ENABLED = process.env.NEXT_PUBLIC_AUTH_ENABLED === 'true';

// App areas that require a signed-in session. The landing page stays public.
const PROTECTED = ['/run', '/candidates', '/schools', '/sources'];

export default function proxy(request: NextRequest) {
  const {pathname} = request.nextUrl;

  if (!AUTH_ENABLED) {
    // Dev: skip all auth gating, just run locale handling.
    return intlMiddleware(request);
  }

  // Strip the locale prefix (/fr/run -> /run) to test against PROTECTED.
  const segments = pathname.split('/').filter(Boolean);
  const maybeLocale = segments[0];
  const hasLocale = (routing.locales as readonly string[]).includes(maybeLocale);
  const locale = hasLocale ? maybeLocale : routing.defaultLocale;
  const appPath = '/' + (hasLocale ? segments.slice(1) : segments).join('/');

  const needsAuth = PROTECTED.some((p) => appPath === p || appPath.startsWith(`${p}/`));
  const hasSession = Boolean(request.cookies.get(SESSION_COOKIE)?.value);

  if (needsAuth && !hasSession) {
    const loginUrl = new URL(`/${locale}/login`, request.url);
    loginUrl.searchParams.set('next', appPath);
    return NextResponse.redirect(loginUrl);
  }

  // Signed-in users landing on /login go straight to the operations room.
  if (appPath === '/login' && hasSession) {
    return NextResponse.redirect(new URL(`/${locale}/run`, request.url));
  }

  return intlMiddleware(request);
}

export const config = {
  // Match all routes except API routes, Next.js internals, and static assets.
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};

import createMiddleware from 'next-intl/middleware';
import {routing} from './i18n/routing';

// Locale detection + redirect middleware.
export default createMiddleware(routing);

export const config = {
  // Match all routes except API routes, Next.js internals, and static assets.
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};

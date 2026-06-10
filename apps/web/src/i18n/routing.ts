import {defineRouting} from 'next-intl/routing';

/**
 * Bilingual routing config — French is default per spec §11.
 * Adding a new locale = add to `locales` array + provide a messages file.
 */
export const routing = defineRouting({
  locales: ['fr', 'en'],
  defaultLocale: 'fr',
  // Prefix the default locale too so URLs are explicit: /fr/... and /en/...
  localePrefix: 'always'
});

export type Locale = (typeof routing.locales)[number];

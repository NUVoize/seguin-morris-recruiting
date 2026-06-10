import {getTranslations, setRequestLocale} from 'next-intl/server';
import {Link} from '@/i18n/navigation';
import {routing} from '@/i18n/routing';

/**
 * Bilingual landing page. The "Open the candidate pipeline" CTA jumps to the
 * real Kanban board which is the first piece of actual recruiter UI.
 */
export default async function HomePage({
  params
}: {
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  setRequestLocale(locale);

  const tBrand = await getTranslations('brand');
  const tHome = await getTranslations('home');

  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 py-16 sm:py-24">
      <div className="w-full max-w-2xl text-center">
        <p className="text-xs uppercase tracking-widest text-neutral-500">
          {tHome('phase')}
        </p>
        <h1 className="mt-6 text-4xl font-semibold tracking-tight text-neutral-900 sm:text-5xl">
          {tBrand('company')}
        </h1>
        <p className="mt-2 text-lg text-neutral-700">{tHome('title')}</p>
        <p className="mt-6 text-base leading-relaxed text-neutral-600">
          {tHome('subtitle')}
        </p>

        <div className="mt-10 flex flex-col items-center gap-6">
          <Link
            href="/candidates"
            className="inline-flex items-center gap-2 rounded-lg bg-neutral-900 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-neutral-700"
          >
            {tHome('open_pipeline')}
            <span aria-hidden>→</span>
          </Link>

          <div className="flex items-center justify-center gap-3 text-sm">
            {routing.locales.map((alt) => (
              <Link
                key={alt}
                href="/"
                locale={alt}
                className={
                  alt === locale
                    ? 'rounded-full bg-neutral-900 px-4 py-1.5 text-white'
                    : 'rounded-full border border-neutral-300 px-4 py-1.5 text-neutral-700 hover:bg-neutral-100'
                }
              >
                {alt.toUpperCase()}
              </Link>
            ))}
          </div>
        </div>

        <footer className="mt-16 text-xs text-neutral-500">
          {tBrand('designed_by')}
        </footer>
      </div>
    </main>
  );
}

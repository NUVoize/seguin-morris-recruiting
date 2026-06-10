import {getTranslations, setRequestLocale} from 'next-intl/server';
import {Link} from '@/i18n/navigation';
import {routing} from '@/i18n/routing';

/**
 * Phase 1 landing page — confirms bilingual routing works and brand chrome renders.
 * Real dashboard arrives in Phase 4.
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

        <div className="mt-10 flex items-center justify-center gap-3 text-sm">
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

        <footer className="mt-16 text-xs text-neutral-500">
          {tBrand('designed_by')}
        </footer>
      </div>
    </main>
  );
}

'use client';

import Image from 'next/image';
import {useTranslations} from 'next-intl';
import {Link, usePathname} from '@/i18n/navigation';
import clsx from 'clsx';
import {LocaleSwitch} from './LocaleSwitch';

/**
 * Shared app shell: top bar with the Seguin Morris wordmark, primary nav,
 * and the locale switch. Makes the pages feel like one product instead of
 * three orphaned screens.
 */
export function AppShell({children}: {children: React.ReactNode}) {
  const t = useTranslations('shell');
  const pathname = usePathname();

  const links = [
    {href: '/run' as const, label: t('nav_agents')},
    {href: '/candidates' as const, label: t('nav_pipeline')},
    {href: '/schools' as const, label: t('nav_schools')},
    {href: '/sources' as const, label: t('nav_sources')}
  ];

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-steel-100 bg-white/90 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-6 px-4 sm:px-6">
          <Link href="/" className="flex shrink-0 items-center" aria-label="Seguin Morris">
            <Image
              src="/brand-seguin-morris.png"
              alt="Seguin Morris"
              width={397}
              height={159}
              priority
              className="h-8 w-auto"
            />
          </Link>

          <nav className="flex items-center gap-1">
            {links.map((l) => {
              const active = pathname.startsWith(l.href);
              return (
                <Link
                  key={l.href}
                  href={l.href}
                  className={clsx(
                    'relative rounded-md px-3 py-1.5 text-sm font-medium transition',
                    active
                      ? 'text-navy'
                      : 'text-steel-500 hover:bg-steel-50 hover:text-steel-700'
                  )}
                >
                  {l.label}
                  {active && (
                    <span className="absolute inset-x-3 -bottom-[13px] h-0.5 rounded-full bg-ember" />
                  )}
                </Link>
              );
            })}
          </nav>

          <div className="ml-auto">
            <LocaleSwitch />
          </div>
        </div>
      </header>

      <div className="flex flex-1 flex-col">{children}</div>

      <footer className="border-t border-steel-100 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <p className="font-display text-xs font-semibold uppercase tracking-[0.18em] text-steel-400">
            Seguin Morris
          </p>
          <p className="text-xs text-steel-400">{t('designed_by')}</p>
        </div>
      </footer>
    </div>
  );
}

'use client';

import {useLocale} from 'next-intl';
import {Link, usePathname} from '@/i18n/navigation';
import {routing} from '@/i18n/routing';
import clsx from 'clsx';

/**
 * Single segmented FR | EN switch. Preserves the current path on toggle
 * (the old landing-page pills always sent you back to "/").
 */
export function LocaleSwitch() {
  const locale = useLocale();
  const pathname = usePathname();

  return (
    <div
      className="inline-flex items-center rounded-full border border-steel-200 bg-white p-0.5"
      role="group"
      aria-label="Language"
    >
      {routing.locales.map((l) => (
        <Link
          key={l}
          href={pathname}
          locale={l}
          className={clsx(
            'rounded-full px-3 py-1 font-display text-[13px] font-semibold uppercase tracking-wider transition',
            l === locale ? 'bg-navy text-white' : 'text-steel-500 hover:text-navy'
          )}
        >
          {l}
        </Link>
      ))}
    </div>
  );
}

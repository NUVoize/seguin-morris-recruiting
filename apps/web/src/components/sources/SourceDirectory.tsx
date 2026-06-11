'use client';

import {useState} from 'react';
import clsx from 'clsx';
import {useLocale, useTranslations} from 'next-intl';

import {sources as sourcesApi, type LeadSource, type SourceType} from '@/lib/api';
import {IconLink} from '@/components/icons';

const TYPE_STYLES: Record<string, string> = {
  government: 'bg-navy/8 text-navy',
  job_board: 'bg-ember/10 text-ember-600',
  social: 'bg-steel-100 text-steel-600',
  association: 'bg-ok-soft text-ok',
  school: 'bg-navy/8 text-navy',
  event: 'bg-steel-100 text-steel-600',
  company_site: 'bg-steel-100 text-steel-600',
  manual: 'bg-steel-100 text-steel-600'
};

const TYPE_ORDER: SourceType[] = [
  'government',
  'job_board',
  'social',
  'association',
  'school',
  'event',
  'company_site',
  'manual'
];

/**
 * Source-policy directory. The toggle is the legal gate for automated
 * collection (spec hard rule #3); enabling requires explicit confirmation
 * and every change is audit-logged server-side.
 */
export function SourceDirectory({initialSources}: {initialSources: LeadSource[]}) {
  const t = useTranslations('sources');
  const locale = useLocale();
  const [items, setItems] = useState<LeadSource[]>(initialSources);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const allowedCount = items.filter((s) => s.allowed_to_scrape).length;

  const sorted = [...items].sort((a, b) => {
    const d = TYPE_ORDER.indexOf(a.source_type) - TYPE_ORDER.indexOf(b.source_type);
    return d !== 0 ? d : a.name.localeCompare(b.name, locale);
  });

  async function handleToggle(source: LeadSource) {
    const enabling = !source.allowed_to_scrape;
    if (enabling && !window.confirm(t('enable_confirm', {name: source.name}))) {
      return;
    }
    setBusyId(source.id);
    setError(null);
    const previous = items;
    setItems((cur) =>
      cur.map((s) => (s.id === source.id ? {...s, allowed_to_scrape: enabling} : s))
    );
    try {
      const updated = await sourcesApi.setScrapePolicy(source.id, enabling);
      setItems((cur) => cur.map((s) => (s.id === updated.id ? updated : s)));
    } catch (err) {
      setItems(previous);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold uppercase tracking-tight text-steel-900">
            {t('title')}
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-steel-500">{t('subtitle')}</p>
        </div>
        <p className="font-mono text-sm tabular-nums text-steel-400">
          {t('allowed_count', {allowed: allowedCount, total: items.length})}
        </p>
      </header>

      <div className="mt-4 rounded-md border-l-2 border-ember bg-white px-4 py-3 text-xs leading-relaxed text-steel-600 shadow-sm">
        {t('policy_note')}
      </div>

      {error && (
        <div className="mt-3 rounded-md border border-danger/30 bg-danger-soft px-3 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      <ul className="mt-5 space-y-2.5">
        {sorted.map((s) => (
          <li
            key={s.id}
            className="flex flex-col gap-3 rounded-xl border border-steel-100 bg-white p-4 shadow-sm sm:flex-row sm:items-center"
          >
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="font-display text-[16px] font-semibold uppercase tracking-wide text-steel-900">
                  {s.name}
                </h2>
                <span
                  className={clsx(
                    'rounded px-1.5 py-0.5 font-mono text-[9.5px] font-semibold uppercase tracking-wide',
                    TYPE_STYLES[s.source_type] ?? 'bg-steel-100 text-steel-600'
                  )}
                >
                  {t(`types.${s.source_type}`)}
                </span>
                <span className="rounded bg-steel-50 px-1.5 py-0.5 font-mono text-[9.5px] uppercase tracking-wide text-steel-500 ring-1 ring-steel-100">
                  {t(`access.${s.access_method}`)}
                </span>
              </div>
              <a
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-1 inline-flex items-center gap-1 break-all text-xs text-navy underline-offset-2 hover:underline"
              >
                <IconLink size={11} className="shrink-0 text-steel-400" />
                {s.url.replace(/^https?:\/\/(www\.)?/, '')}
              </a>
              {s.notes && (
                <p className="mt-1.5 max-w-3xl text-[11.5px] leading-relaxed text-steel-500">
                  {s.notes}
                </p>
              )}
            </div>

            <div className="flex shrink-0 items-center gap-3 sm:flex-col sm:items-end sm:gap-1.5">
              <button
                type="button"
                role="switch"
                aria-checked={s.allowed_to_scrape}
                disabled={busyId === s.id}
                onClick={() => handleToggle(s)}
                className={clsx(
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-navy focus-visible:ring-offset-2',
                  s.allowed_to_scrape ? 'bg-ember' : 'bg-steel-200',
                  busyId === s.id && 'opacity-50'
                )}
              >
                <span
                  className={clsx(
                    'inline-block h-4.5 w-4.5 transform rounded-full bg-white shadow transition-transform',
                    s.allowed_to_scrape ? 'translate-x-[22px]' : 'translate-x-[3px]'
                  )}
                  style={{height: 18, width: 18}}
                />
              </button>
              <span
                className={clsx(
                  'font-mono text-[9.5px] font-semibold uppercase tracking-wide',
                  s.allowed_to_scrape ? 'text-ember' : 'text-steel-400'
                )}
              >
                {s.allowed_to_scrape ? t('scrape_on') : t('scrape_off')}
              </span>
            </div>
          </li>
        ))}
      </ul>

      <p className="mt-8 text-center font-mono text-[10px] text-steel-400">{t('audit_note')}</p>
    </main>
  );
}

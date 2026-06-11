import {getTranslations, setRequestLocale} from 'next-intl/server';
import {cookies} from 'next/headers';
import clsx from 'clsx';

import {apiRequest, type SchoolProgram} from '@/lib/api';
import {IconClock, IconMail, IconPhone, IconPin, IconSchool} from '@/components/icons';

interface Props {
  params: Promise<{locale: string}>;
}

type WindowKey = 'reactivation' | 'ideal' | 'watch' | 'unknown' | 'past';

/** The 90-180 day prospecting rule from the recruiting research. */
function cohortWindow(cohortEnd: string | null): {key: WindowKey; days: number | null} {
  if (!cohortEnd) return {key: 'unknown', days: null};
  const days = Math.floor((new Date(cohortEnd).getTime() - Date.now()) / 86_400_000);
  if (days < 0) return {key: 'past', days};
  if (days <= 30) return {key: 'reactivation', days};
  if (days <= 180) return {key: 'ideal', days};
  return {key: 'watch', days};
}

const WINDOW_STYLES: Record<WindowKey, string> = {
  reactivation: 'bg-ember/10 text-ember-600 ring-1 ring-ember/30',
  ideal: 'bg-ok-soft text-ok ring-1 ring-ok/30',
  watch: 'bg-steel-100 text-steel-600 ring-1 ring-steel-200',
  unknown: 'bg-white text-steel-400 ring-1 ring-steel-200',
  past: 'bg-steel-50 text-steel-300 ring-1 ring-steel-100'
};

const TYPE_ORDER = ['DEP', 'DEC', 'AEC'] as const;

export default async function SchoolsPage({params}: Props) {
  const {locale} = await params;
  setRequestLocale(locale);
  const t = await getTranslations('schools');
  const token = (await cookies()).get('sm_session')?.value ?? null;

  let programs: SchoolProgram[] = [];
  let fetchError: string | null = null;
  try {
    programs = await apiRequest<SchoolProgram[]>('/programs', {query: {limit: 200}, token});
  } catch (err) {
    fetchError = err instanceof Error ? err.message : 'Unknown error';
  }

  if (fetchError) {
    return (
      <main className="flex flex-1 items-center justify-center p-6">
        <div className="max-w-md rounded-xl border border-danger/30 bg-danger-soft p-6 text-center">
          <h2 className="font-display text-lg font-bold uppercase tracking-wide text-danger">
            Backend unreachable
          </h2>
          <p className="mt-2 text-sm text-steel-700">{fetchError}</p>
        </div>
      </main>
    );
  }

  const inWindow = programs.filter((p) =>
    ['ideal', 'reactivation'].includes(cohortWindow(p.cohort_end).key)
  ).length;

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
          {t('in_window_count', {count: inWindow})}
        </p>
      </header>

      {TYPE_ORDER.map((type) => {
        const group = programs.filter((p) => p.program_type === type);
        if (group.length === 0) return null;
        return (
          <section key={type} className="mt-10">
            <div className="flex items-baseline gap-3">
              <h2 className="font-display text-xl font-bold uppercase tracking-wide text-navy">
                {t(`groups.${type}.title`)}
              </h2>
              <span className="font-mono text-xs text-steel-400">{group.length}</span>
            </div>
            <p className="mt-0.5 text-xs text-steel-500">{t(`groups.${type}.description`)}</p>

            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {group.map((p) => {
                const w = cohortWindow(p.cohort_end);
                return (
                  <article
                    key={p.id}
                    className="flex flex-col rounded-xl border border-steel-100 bg-white p-4 shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-display text-[17px] font-semibold uppercase leading-tight tracking-wide text-steel-900">
                        {p.institution_name}
                      </h3>
                      <span className="mt-0.5 shrink-0 text-steel-300">
                        <IconSchool size={16} />
                      </span>
                    </div>
                    <p className="mt-0.5 text-xs text-steel-500">{p.program_name}</p>
                    {p.city && (
                      <p className="mt-1.5 inline-flex items-center gap-1 text-[11px] text-steel-400">
                        <IconPin size={11} />
                        {p.city}
                        {p.province ? `, ${p.province}` : ''}
                      </p>
                    )}

                    <span
                      className={clsx(
                        'mt-3 inline-flex w-fit items-center gap-1.5 rounded px-2 py-1 font-mono text-[10px] font-semibold uppercase tracking-wide',
                        WINDOW_STYLES[w.key]
                      )}
                    >
                      <IconClock size={11} />
                      {w.days != null
                        ? t(`window.${w.key}`, {days: Math.abs(w.days)})
                        : t('window.unknown')}
                    </span>

                    {(p.cohort_start || p.cohort_end) && (
                      <p className="mt-2 font-mono text-[11px] tabular-nums text-steel-500">
                        {p.cohort_start
                          ? new Date(p.cohort_start).toLocaleDateString(locale)
                          : '?'}{' '}
                        {'\u2192'}{' '}
                        {p.cohort_end ? new Date(p.cohort_end).toLocaleDateString(locale) : '?'}
                      </p>
                    )}

                    <div className="mt-3 space-y-1 border-t border-steel-50 pt-3 text-xs">
                      {p.public_contact_name && (
                        <p className="font-medium text-steel-700">{p.public_contact_name}</p>
                      )}
                      {p.public_contact_email && (
                        <a
                          href={`mailto:${p.public_contact_email}`}
                          className="flex items-center gap-1.5 break-all text-navy underline-offset-2 hover:underline"
                        >
                          <IconMail size={12} className="shrink-0 text-steel-400" />
                          {p.public_contact_email}
                        </a>
                      )}
                      {p.public_contact_phone && (
                        <p className="flex items-center gap-1.5 text-steel-600">
                          <IconPhone size={12} className="shrink-0 text-steel-400" />
                          {p.public_contact_phone}
                        </p>
                      )}
                    </div>

                    {p.notes && (
                      <p className="mt-2.5 text-[11px] leading-relaxed text-steel-400">{p.notes}</p>
                    )}
                  </article>
                );
              })}
            </div>
          </section>
        );
      })}

      <p className="mt-10 text-center font-mono text-[10px] text-steel-400">{t('footnote')}</p>
    </main>
  );
}

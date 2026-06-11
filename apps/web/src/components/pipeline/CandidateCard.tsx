'use client';

import clsx from 'clsx';
import {useLocale, useTranslations} from 'next-intl';

import type {Candidate} from '@/lib/api/types';
import {IconClock, IconPin} from '@/components/icons';

import {ScoreRing} from './ScoreRing';
import {candidateSource, daysSince} from './candidateMeta';

interface CandidateCardProps {
  candidate: Candidate;
  onClick: (candidate: Candidate) => void;
  isDragging?: boolean;
}

const SOURCE_STYLES: Record<string, string> = {
  board: 'bg-navy/8 text-navy',
  school: 'bg-ember/10 text-ember-600',
  social: 'bg-steel-100 text-steel-600',
  other: 'bg-steel-100 text-steel-600'
};

/**
 * Candidate card, recruiter-product style: identity, fit ring,
 * source-of-discovery badge, region, last-activity age.
 */
export function CandidateCard({candidate, onClick, isDragging}: CandidateCardProps) {
  const t = useTranslations('pipeline.card');
  const locale = useLocale();

  const displayName = candidate.full_name || t('no_name');
  const title = candidate.current_title || t('no_title');
  const region = candidate.region || t('no_region');
  const score = candidate.fit_score;
  const source = candidateSource(candidate);
  const days = daysSince(candidate.updated_at);

  return (
    <button
      type="button"
      onClick={() => onClick(candidate)}
      className={clsx(
        'group w-full rounded-lg border border-steel-100 bg-white p-3 text-left shadow-sm transition',
        'hover:-translate-y-px hover:border-steel-200 hover:shadow-md',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-navy focus-visible:ring-offset-1',
        isDragging ? 'opacity-40' : 'opacity-100'
      )}
    >
      <div className="flex items-start justify-between gap-2.5">
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13.5px] font-semibold leading-snug text-steel-900">
            {displayName}
          </p>
          <p className="mt-0.5 truncate text-xs text-steel-500">{title}</p>
        </div>
        {score != null && <ScoreRing score={score} />}
      </div>

      <div className="mt-2.5 flex items-center gap-1.5">
        {source && (
          <span
            className={clsx(
              'inline-flex items-center rounded px-1.5 py-0.5 font-mono text-[9.5px] font-semibold uppercase tracking-wide',
              SOURCE_STYLES[source.kind]
            )}
          >
            {source.label}
          </span>
        )}
        <span className="inline-flex min-w-0 items-center gap-1 text-[11px] text-steel-400">
          <IconPin size={11} className="shrink-0" />
          <span className="truncate">{region}</span>
        </span>
        {days != null && (
          <span
            className={clsx(
              'ml-auto inline-flex shrink-0 items-center gap-1 rounded px-1.5 py-0.5 font-mono text-[10px] tabular-nums',
              days > 14
                ? 'bg-danger-soft text-danger'
                : days > 7
                  ? 'bg-warn-soft text-warn'
                  : 'text-steel-400'
            )}
            title={new Date(candidate.updated_at).toLocaleDateString(locale)}
          >
            <IconClock size={10.5} />
            {days}{t('days_suffix')}
          </span>
        )}
      </div>
    </button>
  );
}

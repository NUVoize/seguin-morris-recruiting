'use client';

import clsx from 'clsx';
import {useTranslations} from 'next-intl';

import type {Candidate} from '@/lib/api/types';

interface CandidateCardProps {
  candidate: Candidate;
  onClick: (candidate: Candidate) => void;
  isDragging?: boolean;
}

/**
 * One candidate displayed as a draggable card inside a Kanban column.
 * Pure presentation — drag wiring lives in the parent SortableCandidateCard.
 */
export function CandidateCard({candidate, onClick, isDragging}: CandidateCardProps) {
  const t = useTranslations('pipeline.card');

  const displayName = candidate.full_name || t('no_name');
  const region = candidate.region || t('no_region');
  const title = candidate.current_title || t('no_title');
  const score = candidate.fit_score;

  return (
    <button
      type="button"
      onClick={() => onClick(candidate)}
      className={clsx(
        'group w-full text-left rounded-lg border bg-white p-3 shadow-sm transition',
        'hover:border-neutral-300 hover:shadow-md focus:outline-none focus-visible:ring-2',
        'focus-visible:ring-neutral-900 focus-visible:ring-offset-1',
        isDragging ? 'opacity-40' : 'opacity-100'
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-neutral-900">{displayName}</p>
          <p className="mt-0.5 truncate text-xs text-neutral-500">{title}</p>
        </div>
        {score != null && (
          <span
            className={clsx(
              'shrink-0 rounded-full px-2 py-0.5 text-xs font-medium',
              score >= 80
                ? 'bg-emerald-50 text-emerald-700'
                : score >= 50
                  ? 'bg-amber-50 text-amber-700'
                  : 'bg-neutral-100 text-neutral-600'
            )}
            aria-label={`Fit score ${score}`}
          >
            {score}
          </span>
        )}
      </div>
      <p className="mt-2 truncate text-xs text-neutral-500">{region}</p>
    </button>
  );
}

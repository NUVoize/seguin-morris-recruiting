'use client';

import {useTranslations} from 'next-intl';

import {PIPELINE_STAGES, type Candidate, type PipelineStage} from '@/lib/api/types';

interface CandidateDetailPanelProps {
  candidate: Candidate;
  onClose: () => void;
  onChangeStage: (stage: PipelineStage) => Promise<void> | void;
  onDelete: () => Promise<void> | void;
}

/**
 * Slide-out detail panel — opens when a card is clicked.
 * Plain fixed-position div + backdrop. No portal needed at this scale.
 */
export function CandidateDetailPanel({
  candidate,
  onClose,
  onChangeStage,
  onDelete
}: CandidateDetailPanelProps) {
  const tDetail = useTranslations('pipeline.detail');
  const tStages = useTranslations('pipeline.stages');
  const tCommon = useTranslations('common');

  const handleDelete = () => {
    if (window.confirm(tDetail('delete_confirm'))) {
      void onDelete();
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 z-40 bg-neutral-900/30 backdrop-blur-sm"
        aria-hidden
      />

      {/* Panel */}
      <aside
        role="dialog"
        aria-labelledby="candidate-detail-title"
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col overflow-y-auto border-l border-neutral-200 bg-white shadow-xl"
      >
        <header className="flex items-start justify-between gap-4 border-b border-neutral-200 px-6 py-5">
          <div className="min-w-0 flex-1">
            <p className="text-xs uppercase tracking-widest text-neutral-500">
              {tDetail('title')}
            </p>
            <h2 id="candidate-detail-title" className="mt-1 truncate text-xl font-semibold">
              {candidate.full_name || tDetail('title')}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 rounded-md p-1.5 text-neutral-500 hover:bg-neutral-100"
            aria-label={tCommon('close')}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-5 w-5"
            >
              <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
            </svg>
          </button>
        </header>

        <div className="space-y-5 px-6 py-5">
          {/* Fit score */}
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-neutral-500">
              {tDetail('fit_score')}
            </p>
            <p className="mt-1 text-2xl font-semibold text-neutral-900">
              {candidate.fit_score ?? '—'}
              {candidate.fit_label && (
                <span className="ml-2 text-sm font-normal text-neutral-500">
                  · {candidate.fit_label}
                </span>
              )}
            </p>
            {candidate.fit_summary && (
              <p className="mt-1 text-sm text-neutral-700">{candidate.fit_summary}</p>
            )}
            <p className="mt-2 text-xs italic text-neutral-500">{tDetail('vetting_reminder')}</p>
          </div>

          {/* Stage selector */}
          <div>
            <label
              htmlFor="pipeline-stage"
              className="block text-xs font-medium uppercase tracking-wider text-neutral-500"
            >
              {tDetail('pipeline_status')}
            </label>
            <select
              id="pipeline-stage"
              value={candidate.pipeline_status}
              onChange={(e) => onChangeStage(e.target.value as PipelineStage)}
              className="mt-1 w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm focus:border-neutral-900 focus:outline-none focus:ring-1 focus:ring-neutral-900"
            >
              {PIPELINE_STAGES.map((stage) => (
                <option key={stage} value={stage}>
                  {tStages(stage)}
                </option>
              ))}
            </select>
          </div>

          {/* Field grid */}
          <dl className="grid grid-cols-1 gap-4 text-sm">
            <Field label={tDetail('region')} value={candidate.region} />
            <Field label={tDetail('title_label')} value={candidate.current_title} />
            <Field label={tDetail('email')} value={candidate.contact_email} />
            <Field label={tDetail('phone')} value={candidate.contact_phone} />
            <Field
              label={tDetail('profile_url')}
              value={candidate.profile_url}
              renderValue={(v) => (
                <a
                  href={v}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="break-all text-blue-600 underline-offset-2 hover:underline"
                >
                  {v}
                </a>
              )}
            />
            <Field label={tDetail('candidate_type')} value={candidate.candidate_type} />
            <Field label={tDetail('consent_status')} value={candidate.consent_status} />
            <Field
              label={tDetail('created_at')}
              value={new Date(candidate.created_at).toLocaleString()}
            />
          </dl>
        </div>

        <footer className="mt-auto border-t border-neutral-200 px-6 py-4">
          <button
            type="button"
            onClick={handleDelete}
            className="text-sm font-medium text-red-700 hover:text-red-900"
          >
            {tDetail('delete_candidate')}
          </button>
        </footer>
      </aside>
    </>
  );
}

function Field({
  label,
  value,
  renderValue
}: {
  label: string;
  value: string | null | undefined;
  renderValue?: (v: string) => React.ReactNode;
}) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wider text-neutral-500">{label}</dt>
      <dd className="mt-0.5 text-sm text-neutral-900">
        {value ? (renderValue ? renderValue(value) : value) : <span className="text-neutral-400">—</span>}
      </dd>
    </div>
  );
}

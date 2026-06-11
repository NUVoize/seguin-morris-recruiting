'use client';

import {useLocale, useTranslations} from 'next-intl';

import {PIPELINE_STAGES, type Candidate, type PipelineStage} from '@/lib/api/types';
import {IconClock, IconLink, IconMail, IconPhone, IconPin, IconX} from '@/components/icons';

import {ScoreRing} from './ScoreRing';
import {candidateSource} from './candidateMeta';

interface CandidateDetailPanelProps {
  candidate: Candidate;
  onClose: () => void;
  onChangeStage: (stage: PipelineStage) => Promise<void> | void;
  onDelete: () => Promise<void> | void;
}

/**
 * Slide-out candidate sheet. Navy identity band, fit score ring with the
 * advisory note (hard rule), stage control, contact rows, metadata.
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
  const locale = useLocale();

  const source = candidateSource(candidate);

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
        className="fixed inset-0 z-40 bg-navy-950/40 backdrop-blur-[2px]"
        aria-hidden
      />

      {/* Panel */}
      <aside
        role="dialog"
        aria-labelledby="candidate-detail-title"
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col overflow-y-auto bg-white shadow-2xl"
      >
        {/* Identity band */}
        <header className="bg-navy-950 px-6 pb-5 pt-5 text-white">
          <div className="flex items-start justify-between gap-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-steel-400">
              {tDetail('title')}
            </p>
            <button
              type="button"
              onClick={onClose}
              className="shrink-0 rounded-md p-1.5 text-steel-400 transition hover:bg-white/10 hover:text-white"
              aria-label={tCommon('close')}
            >
              <IconX size={16} />
            </button>
          </div>
          <h2
            id="candidate-detail-title"
            className="mt-2 truncate font-display text-3xl font-bold uppercase tracking-tight"
          >
            {candidate.full_name || tDetail('title')}
          </h2>
          <div className="mt-1.5 flex flex-wrap items-center gap-2 text-sm text-steel-300">
            {candidate.current_title && <span>{candidate.current_title}</span>}
            {candidate.region && (
              <span className="inline-flex items-center gap-1">
                <IconPin size={12} />
                {candidate.region}
              </span>
            )}
            {source && (
              <span className="rounded bg-white/10 px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-ember-400">
                {source.label}
              </span>
            )}
          </div>
        </header>

        <div className="space-y-6 px-6 py-6">
          {/* Fit score */}
          <section>
            <SectionLabel>{tDetail('fit_score')}</SectionLabel>
            <div className="mt-2.5 flex items-start gap-4">
              {candidate.fit_score != null ? (
                <ScoreRing score={candidate.fit_score} size={64} stroke={5} />
              ) : (
                <span className="flex h-16 w-16 items-center justify-center rounded-full border-2 border-dashed border-steel-200 font-mono text-xs text-steel-300">
                  {'\u2014'}
                </span>
              )}
              <div className="min-w-0 flex-1 pt-1">
                {candidate.fit_label && (
                  <p className="font-display text-lg font-semibold uppercase tracking-wide text-steel-800">
                    {candidate.fit_label}
                  </p>
                )}
                {candidate.fit_summary && (
                  <p className="mt-1 text-sm leading-relaxed text-steel-600">
                    {candidate.fit_summary}
                  </p>
                )}
              </div>
            </div>
            <p className="mt-3 rounded-md border-l-2 border-ember bg-steel-50 px-3 py-2 text-xs leading-relaxed text-steel-600">
              {tDetail('vetting_reminder')}
            </p>
          </section>

          {/* Stage */}
          <section>
            <label htmlFor="pipeline-stage">
              <SectionLabel>{tDetail('pipeline_status')}</SectionLabel>
            </label>
            <select
              id="pipeline-stage"
              value={candidate.pipeline_status}
              onChange={(e) => onChangeStage(e.target.value as PipelineStage)}
              className="mt-2 w-full rounded-lg border border-steel-200 bg-white px-3 py-2.5 text-sm font-medium text-steel-800 transition focus:border-navy focus:outline-none focus:ring-1 focus:ring-navy"
            >
              {PIPELINE_STAGES.map((stage) => (
                <option key={stage} value={stage}>
                  {tStages(stage)}
                </option>
              ))}
            </select>
          </section>

          {/* Contact */}
          <section>
            <SectionLabel>{tDetail('contact_section')}</SectionLabel>
            <div className="mt-2 divide-y divide-steel-50 rounded-lg border border-steel-100">
              <ContactRow
                icon={<IconMail size={14} />}
                value={candidate.contact_email}
                href={candidate.contact_email ? `mailto:${candidate.contact_email}` : undefined}
              />
              <ContactRow
                icon={<IconPhone size={14} />}
                value={candidate.contact_phone}
                href={candidate.contact_phone ? `tel:${candidate.contact_phone}` : undefined}
              />
              <ContactRow
                icon={<IconLink size={14} />}
                value={candidate.profile_url}
                href={candidate.profile_url ?? undefined}
                external
              />
            </div>
          </section>

          {/* Metadata */}
          <section>
            <SectionLabel>{tDetail('meta_section')}</SectionLabel>
            <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
              <Meta label={tDetail('candidate_type')} value={candidate.candidate_type} />
              <Meta label={tDetail('consent_status')} value={candidate.consent_status} />
              <Meta
                label={tDetail('created_at')}
                value={new Date(candidate.created_at).toLocaleDateString(locale)}
              />
              <Meta
                label={tDetail('last_seen_at')}
                value={
                  candidate.last_seen_at
                    ? new Date(candidate.last_seen_at).toLocaleDateString(locale)
                    : null
                }
                icon={<IconClock size={11} />}
              />
            </dl>
          </section>
        </div>

        <footer className="mt-auto border-t border-steel-100 px-6 py-4">
          <button
            type="button"
            onClick={handleDelete}
            className="text-sm font-medium text-danger transition hover:text-danger/80"
          >
            {tDetail('delete_candidate')}
          </button>
        </footer>
      </aside>
    </>
  );
}

function SectionLabel({children}: {children: React.ReactNode}) {
  return (
    <span className="font-mono text-[10px] font-medium uppercase tracking-[0.2em] text-steel-400">
      {children}
    </span>
  );
}

function ContactRow({
  icon,
  value,
  href,
  external
}: {
  icon: React.ReactNode;
  value: string | null | undefined;
  href?: string;
  external?: boolean;
}) {
  const inner = (
    <span className="flex min-w-0 items-center gap-2.5 px-3 py-2.5">
      <span className="shrink-0 text-steel-400">{icon}</span>
      {value ? (
        <span className="truncate text-sm text-steel-800">{value}</span>
      ) : (
        <span className="text-sm text-steel-300">{'\u2014'}</span>
      )}
    </span>
  );

  if (value && href) {
    return (
      <a
        href={href}
        target={external ? '_blank' : undefined}
        rel={external ? 'noopener noreferrer' : undefined}
        className="block transition hover:bg-steel-50"
      >
        {inner}
      </a>
    );
  }
  return <div>{inner}</div>;
}

function Meta({
  label,
  value,
  icon
}: {
  label: string;
  value: string | null | undefined;
  icon?: React.ReactNode;
}) {
  return (
    <div>
      <dt className="font-mono text-[10px] font-medium uppercase tracking-wider text-steel-400">
        {label}
      </dt>
      <dd className="mt-0.5 flex items-center gap-1 text-sm text-steel-800">
        {icon && <span className="text-steel-400">{icon}</span>}
        {value ?? <span className="text-steel-300">{'\u2014'}</span>}
      </dd>
    </div>
  );
}

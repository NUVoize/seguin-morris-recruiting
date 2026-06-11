'use client';

import {useDraggable, useDroppable} from '@dnd-kit/core';
import {CSS} from '@dnd-kit/utilities';
import clsx from 'clsx';
import {useTranslations} from 'next-intl';

import type {Candidate, PipelineStage} from '@/lib/api/types';

import {CandidateCard} from './CandidateCard';

interface KanbanColumnProps {
  stage: PipelineStage;
  candidates: Candidate[];
  onCardClick: (candidate: Candidate) => void;
}

/** Stage groups get a colored top rail: intake / active / won / closed. */
const STAGE_RAIL: Record<PipelineStage, string> = {
  new: 'bg-steel-300',
  to_review: 'bg-steel-300',
  contacted: 'bg-navy-500',
  interested: 'bg-navy-500',
  interview: 'bg-ember',
  offer: 'bg-ember',
  hired: 'bg-ok',
  rejected: 'bg-steel-200',
  archived: 'bg-steel-200'
};

export function KanbanColumn({stage, candidates, onCardClick}: KanbanColumnProps) {
  const tStages = useTranslations('pipeline.stages');
  const tPipeline = useTranslations('pipeline');

  const {setNodeRef, isOver} = useDroppable({
    id: `column-${stage}`,
    data: {stage}
  });

  return (
    <div
      ref={setNodeRef}
      className={clsx(
        'flex h-full min-w-[264px] flex-col overflow-hidden rounded-xl border transition-colors',
        isOver ? 'border-navy bg-steel-100' : 'border-steel-100 bg-steel-50/70'
      )}
    >
      <div className={clsx('h-[3px] shrink-0', STAGE_RAIL[stage])} aria-hidden />
      <header className="flex items-center justify-between px-3 py-2.5">
        <h3 className="font-display text-[13px] font-semibold uppercase tracking-wider text-steel-700">
          {tStages(stage)}
        </h3>
        <span className="rounded-full bg-white px-2 py-0.5 font-mono text-[11px] font-medium tabular-nums text-steel-500 ring-1 ring-steel-100">
          {candidates.length}
        </span>
      </header>

      <div className="flex flex-1 flex-col gap-2 overflow-y-auto px-2 pb-2">
        {candidates.length === 0 ? (
          <p className="rounded-lg border border-dashed border-steel-200 px-1 py-5 text-center text-xs text-steel-300">
            {tPipeline('empty_column')}
          </p>
        ) : (
          candidates.map((candidate) => (
            <DraggableCandidate key={candidate.id} candidate={candidate} onClick={onCardClick} />
          ))
        )}
      </div>
    </div>
  );
}

function DraggableCandidate({
  candidate,
  onClick
}: {
  candidate: Candidate;
  onClick: (c: Candidate) => void;
}) {
  const {attributes, listeners, setNodeRef, transform, isDragging} = useDraggable({
    id: candidate.id,
    data: {candidate}
  });

  const style = transform
    ? {
        transform: CSS.Translate.toString(transform),
        zIndex: isDragging ? 50 : 'auto'
      }
    : undefined;

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <CandidateCard candidate={candidate} onClick={onClick} isDragging={isDragging} />
    </div>
  );
}

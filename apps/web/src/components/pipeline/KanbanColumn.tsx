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

/**
 * One column = one pipeline stage. Acts as a drop target via useDroppable.
 * Cards inside register themselves as draggable.
 */
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
        'flex h-full min-w-[260px] flex-col rounded-lg border bg-neutral-50/60 transition-colors',
        isOver ? 'border-neutral-900 bg-neutral-100' : 'border-neutral-200'
      )}
    >
      <header className="flex items-center justify-between border-b border-neutral-200 px-3 py-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-700">
          {tStages(stage)}
        </h3>
        <span className="rounded-full bg-white px-2 py-0.5 text-xs font-medium text-neutral-600 ring-1 ring-neutral-200">
          {candidates.length}
        </span>
      </header>

      <div className="flex flex-1 flex-col gap-2 overflow-y-auto p-2">
        {candidates.length === 0 ? (
          <p className="px-1 py-4 text-center text-xs text-neutral-400">
            {tPipeline('empty_column')}
          </p>
        ) : (
          candidates.map((candidate) => (
            <DraggableCandidate
              key={candidate.id}
              candidate={candidate}
              onClick={onCardClick}
            />
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

'use client';

import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent
} from '@dnd-kit/core';
import {useTranslations} from 'next-intl';
import {useCallback, useEffect, useMemo, useState} from 'react';

import {candidates as candidatesApi} from '@/lib/api';
import {PIPELINE_STAGES, type Candidate, type PipelineStage} from '@/lib/api/types';

import {CandidateCard} from './CandidateCard';
import {CandidateDetailPanel} from './CandidateDetailPanel';
import {KanbanColumn} from './KanbanColumn';

interface KanbanBoardProps {
  initialCandidates: Candidate[];
}

/**
 * Top-level Kanban board.
 * - State is held client-side; mutations call the API and optimistically update.
 * - Drag a card across columns to change its pipeline_status.
 * - Click a card to open the detail panel.
 */
export function KanbanBoard({initialCandidates}: KanbanBoardProps) {
  const tPipeline = useTranslations('pipeline');
  const tCommon = useTranslations('common');

  const [items, setItems] = useState<Candidate[]>(initialCandidates);
  const [selected, setSelected] = useState<Candidate | null>(null);
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // 8px activation distance keeps card *clicks* from being treated as drags.
  const sensors = useSensors(
    useSensor(PointerSensor, {activationConstraint: {distance: 8}}),
    useSensor(KeyboardSensor)
  );

  const grouped = useMemo(() => {
    const map: Record<PipelineStage, Candidate[]> = Object.fromEntries(
      PIPELINE_STAGES.map((s) => [s, [] as Candidate[]])
    ) as Record<PipelineStage, Candidate[]>;
    for (const c of items) {
      map[c.pipeline_status].push(c);
    }
    return map;
  }, [items]);

  const draggingCandidate = useMemo(
    () => items.find((c) => c.id === draggingId) ?? null,
    [items, draggingId]
  );

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setDraggingId(String(event.active.id));
  }, []);

  const handleDragEnd = useCallback(
    async (event: DragEndEvent) => {
      setDraggingId(null);
      const candidateId = String(event.active.id);
      const overData = event.over?.data?.current as {stage?: PipelineStage} | undefined;
      const newStage = overData?.stage;
      if (!newStage) return;

      const current = items.find((c) => c.id === candidateId);
      if (!current || current.pipeline_status === newStage) return;

      // Optimistic update
      const previous = current.pipeline_status;
      setItems((prev) =>
        prev.map((c) => (c.id === candidateId ? {...c, pipeline_status: newStage} : c))
      );
      setSelected((s) => (s?.id === candidateId ? {...s, pipeline_status: newStage} : s));

      try {
        await candidatesApi.setPipelineStage(candidateId, newStage);
      } catch (err) {
        // Rollback
        setItems((prev) =>
          prev.map((c) => (c.id === candidateId ? {...c, pipeline_status: previous} : c))
        );
        setSelected((s) => (s?.id === candidateId ? {...s, pipeline_status: previous} : s));
        setErrorMessage(err instanceof Error ? err.message : 'Unknown error');
      }
    },
    [items]
  );

  const handlePanelStageChange = useCallback(
    async (newStage: PipelineStage) => {
      if (!selected || selected.pipeline_status === newStage) return;
      const previous = selected.pipeline_status;

      // Optimistic update
      setSelected({...selected, pipeline_status: newStage});
      setItems((prev) =>
        prev.map((c) => (c.id === selected.id ? {...c, pipeline_status: newStage} : c))
      );

      try {
        await candidatesApi.setPipelineStage(selected.id, newStage);
      } catch (err) {
        setSelected({...selected, pipeline_status: previous});
        setItems((prev) =>
          prev.map((c) => (c.id === selected.id ? {...c, pipeline_status: previous} : c))
        );
        setErrorMessage(err instanceof Error ? err.message : 'Unknown error');
      }
    },
    [selected]
  );

  const handlePanelDelete = useCallback(async () => {
    if (!selected) return;
    const removed = selected;
    setSelected(null);
    setItems((prev) => prev.filter((c) => c.id !== removed.id));

    try {
      await candidatesApi.remove(removed.id);
    } catch (err) {
      // Restore on failure
      setItems((prev) => [...prev, removed]);
      setErrorMessage(err instanceof Error ? err.message : 'Unknown error');
    }
  }, [selected]);

  // Auto-dismiss error after a few seconds
  useEffect(() => {
    if (!errorMessage) return;
    const t = setTimeout(() => setErrorMessage(null), 4000);
    return () => clearTimeout(t);
  }, [errorMessage]);

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col">
      <header className="flex flex-wrap items-baseline justify-between gap-2 px-6 pb-4 pt-2">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900">{tPipeline('title')}</h1>
          <p className="mt-1 text-sm text-neutral-600">{tPipeline('subtitle')}</p>
        </div>
        <p className="text-sm text-neutral-500">
          {tPipeline('total_candidates', {count: items.length})}
        </p>
      </header>

      {errorMessage && (
        <div className="mx-6 mb-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900">
          {tCommon('error')}: {errorMessage}
        </div>
      )}

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex flex-1 gap-3 overflow-x-auto px-6 pb-6">
          {PIPELINE_STAGES.map((stage) => (
            <KanbanColumn
              key={stage}
              stage={stage}
              candidates={grouped[stage]}
              onCardClick={setSelected}
            />
          ))}
        </div>

        <DragOverlay dropAnimation={null}>
          {draggingCandidate ? (
            <div className="w-[240px] rotate-2">
              <CandidateCard candidate={draggingCandidate} onClick={() => {}} />
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {selected && (
        <CandidateDetailPanel
          candidate={selected}
          onClose={() => setSelected(null)}
          onChangeStage={handlePanelStageChange}
          onDelete={handlePanelDelete}
        />
      )}
    </div>
  );
}

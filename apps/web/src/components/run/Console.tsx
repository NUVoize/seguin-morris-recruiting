'use client';

import {useEffect, useMemo, useRef} from 'react';
import clsx from 'clsx';
import type {AgentRun, AgentType} from '@/lib/api';

const AGENT_TAGS: Partial<Record<AgentType, string>> = {
  employment_source: 'SRC',
  school_pipeline: 'EDU',
  lead_enrichment: 'ENR',
  candidate_vetting: 'VET',
  fit_ranking: 'RNK'
};

interface ConsoleProps {
  order: AgentType[];
  runsByType: Map<AgentType, AgentRun>;
  waitingLabel: string;
  titleLabel: string;
  live: boolean;
}

interface Line {
  ts: string;
  agent: AgentType;
  message: string;
}

/**
 * One unified telemetry console. All agent steps are merged into a single
 * chronological feed with a fixed-width agent tag — the way a real ops
 * console (CI pipeline, deploy log) reads. Replaces five cramped dark
 * boxes inside white cards.
 */
export function Console({order, runsByType, waitingLabel, titleLabel, live}: ConsoleProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const stickToBottom = useRef(true);

  const lines: Line[] = useMemo(() => {
    const all: Line[] = [];
    for (const agent of order) {
      const run = runsByType.get(agent);
      for (const step of run?.output?.steps ?? []) {
        all.push({ts: step.ts, agent, message: step.message});
      }
    }
    all.sort((a, b) => (a.ts < b.ts ? -1 : a.ts > b.ts ? 1 : 0));
    return all;
  }, [order, runsByType]);

  // Auto-scroll, but respect a user who scrolled up to read.
  useEffect(() => {
    const el = scrollRef.current;
    if (el && stickToBottom.current) el.scrollTop = el.scrollHeight;
  }, [lines.length]);

  function handleScroll() {
    const el = scrollRef.current;
    if (!el) return;
    stickToBottom.current = el.scrollHeight - el.scrollTop - el.clientHeight < 48;
  }

  const lastIndex = lines.length - 1;

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-xl border border-steel-800 bg-navy-950">
      <div className="flex items-center gap-2 border-b border-steel-800 px-4 py-2.5">
        <span className="flex gap-1.5" aria-hidden>
          <span className="h-2 w-2 rounded-full bg-steel-700" />
          <span className="h-2 w-2 rounded-full bg-steel-700" />
          <span className={clsx('h-2 w-2 rounded-full', live ? 'sm-blink bg-ember' : 'bg-ok')} />
        </span>
        <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-steel-500">
          {titleLabel}
        </span>
        {live && (
          <span className="ml-auto font-mono text-[10px] uppercase tracking-wider text-ember">
            ● LIVE
          </span>
        )}
      </div>

      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="sm-console min-h-0 flex-1 overflow-y-auto px-4 py-3 font-mono text-[12px] leading-[1.7]"
      >
        {lines.length === 0 ? (
          <p className="text-steel-600">{waitingLabel}</p>
        ) : (
          lines.map((line, i) => (
            <div
              key={`${line.ts}-${i}`}
              className={clsx('flex gap-3 whitespace-pre-wrap', i === lastIndex && 'sm-rise')}
            >
              <span className="shrink-0 tabular-nums text-steel-600">{line.ts.slice(11, 19)}</span>
              <span
                className={clsx(
                  'w-9 shrink-0 font-semibold',
                  i === lastIndex && live ? 'text-ember' : 'text-navy-500'
                )}
              >
                {AGENT_TAGS[line.agent] ?? '···'}
              </span>
              <span className="text-steel-200">{line.message}</span>
            </div>
          ))
        )}
        {live && <span className="sm-blink inline-block h-3.5 w-2 translate-y-0.5 bg-ember" aria-hidden />}
      </div>
    </div>
  );
}

'use client';

import {useEffect, useRef} from 'react';
import type {AgentRun, AgentStep, AgentType} from '@/lib/api';

interface Props {
  agentType: AgentType;
  displayName: string;
  icon: string;
  run: AgentRun | null;
  /** UI labels coming from next-intl (already translated). */
  labels: {
    pending: string;
    running: string;
    completed: string;
    failed: string;
    waiting: string;
  };
}

/**
 * One agent card in the live theater.
 * Renders a status pill, count chips from output.counts, and a live log feed
 * of step messages that auto-scrolls to the latest line.
 */
export function AgentCard({agentType, displayName, icon, run, labels}: Props) {
  const logRef = useRef<HTMLDivElement>(null);
  const status = run?.status ?? 'pending';
  const steps: AgentStep[] = run?.output?.steps ?? [];
  const counts = run?.output?.counts ?? {};

  // Auto-scroll the log to the latest step.
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [steps.length]);

  const statusStyles = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
  const statusLabel =
    status === 'completed'
      ? labels.completed
      : status === 'running'
        ? labels.running
        : status === 'failed'
          ? labels.failed
          : labels.pending;

  return (
    <div
      className={`rounded-xl border bg-white p-5 shadow-sm transition ${
        status === 'running' ? 'border-amber-300 ring-2 ring-amber-100' : 'border-neutral-200'
      }`}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl leading-none" aria-hidden>
          {icon}
        </span>
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-semibold text-neutral-900">{displayName}</div>
          <div className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            {agentType.replace(/_/g, ' ')}
          </div>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles}`}
        >
          {status === 'running' && (
            <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-amber-500" />
          )}
          {statusLabel}
        </span>
      </div>

      {Object.keys(counts).length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {Object.entries(counts).map(([key, value]) => (
            <span
              key={key}
              className="inline-flex items-center rounded-md bg-neutral-100 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-neutral-700"
            >
              {key.replace(/_/g, ' ')}: <span className="ml-1 font-semibold text-neutral-900">{value}</span>
            </span>
          ))}
        </div>
      )}

      <div
        ref={logRef}
        className="mt-4 h-32 overflow-y-auto rounded-md bg-neutral-950 p-3 font-mono text-[11px] leading-relaxed text-neutral-200"
      >
        {steps.length === 0 ? (
          <div className="text-neutral-500">{labels.waiting}</div>
        ) : (
          steps.map((step, i) => (
            <div key={i} className="flex gap-2 py-0.5">
              <span className="shrink-0 text-neutral-500">{step.ts.slice(11, 19)}</span>
              <span className="shrink-0" aria-hidden>
                {step.icon}
              </span>
              <span className="text-neutral-100">{step.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

const STATUS_STYLES: Record<string, string> = {
  pending: 'bg-neutral-100 text-neutral-600',
  running: 'bg-amber-50 text-amber-800',
  completed: 'bg-emerald-50 text-emerald-800',
  failed: 'bg-red-50 text-red-800',
  cancelled: 'bg-neutral-100 text-neutral-500'
};
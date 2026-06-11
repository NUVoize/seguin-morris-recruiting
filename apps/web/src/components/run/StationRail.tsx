'use client';

import clsx from 'clsx';
import type {AgentRun, AgentType} from '@/lib/api';
import {AGENT_ICONS, IconCheck, IconX} from '@/components/icons';

export interface StationLabels {
  pending: string;
  running: string;
  completed: string;
  failed: string;
  countLabel: (key: string) => string;
}

interface StationRailProps {
  order: AgentType[];
  runsByType: Map<AgentType, AgentRun>;
  agentName: (a: AgentType) => string;
  labels: StationLabels;
}

/**
 * The signature element of the run page: a vertical rail of agent
 * stations connected by a flow line. While the pipeline runs, an
 * ember pulse travels down the connector into the active station.
 */
export function StationRail({order, runsByType, agentName, labels}: StationRailProps) {
  return (
    <ol className="relative">
      {order.map((agent, i) => {
        const run = runsByType.get(agent) ?? null;
        const status = run?.status ?? 'pending';
        const isLast = i === order.length - 1;
        return (
          <li key={agent} className="relative pl-9 pb-2">
            {!isLast && (
              <span
                className="absolute left-[13px] top-7 bottom-[-6px] w-px overflow-hidden bg-steel-700"
                aria-hidden
              >
                {status === 'completed' && (
                  <span className="absolute inset-0 bg-ember/60" />
                )}
                {status === 'running' && (
                  <span className="sm-rail-pulse absolute left-0 h-8 w-px bg-gradient-to-b from-transparent via-ember to-transparent" />
                )}
              </span>
            )}
            <StationNode agent={agent} status={status} />
            <Station
              agent={agent}
              run={run}
              status={status}
              name={agentName(agent)}
              labels={labels}
            />
          </li>
        );
      })}
    </ol>
  );
}

function StationNode({agent, status}: {agent: AgentType; status: string}) {
  return (
    <span
      className={clsx(
        'absolute left-0 top-0 flex h-7 w-7 items-center justify-center rounded-full border transition-colors duration-300',
        status === 'running' && 'border-ember bg-ember/15 text-ember',
        status === 'completed' && 'border-ok/60 bg-ok/10 text-ok',
        status === 'failed' && 'border-danger bg-danger/10 text-danger',
        (status === 'pending' || status === 'cancelled') &&
          'border-steel-700 bg-steel-800 text-steel-500'
      )}
      aria-hidden
    >
      {status === 'completed' ? (
        <IconCheck size={13} />
      ) : status === 'failed' ? (
        <IconX size={13} />
      ) : (
        (() => {
          const Icon = AGENT_ICONS[agent];
          return Icon ? <Icon size={13} className={status === 'running' ? 'sm-blink' : ''} /> : null;
        })()
      )}
    </span>
  );
}

function Station({
  agent,
  run,
  status,
  name,
  labels
}: {
  agent: AgentType;
  run: AgentRun | null;
  status: string;
  name: string;
  labels: StationLabels;
}) {
  const counts = run?.output?.counts ?? {};
  const entries = Object.entries(counts).filter(([, v]) => v > 0);
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
      className={clsx(
        'rounded-lg border px-3 py-2.5 transition-colors duration-300',
        status === 'running' && 'sm-sweep border-ember/50 bg-steel-800',
        status === 'completed' && 'border-steel-700 bg-steel-800/60',
        status === 'failed' && 'border-danger/50 bg-danger/5',
        (status === 'pending' || status === 'cancelled') && 'border-steel-800 bg-transparent'
      )}
    >
      <div className="flex items-baseline justify-between gap-2">
        <span
          className={clsx(
            'font-display text-[15px] font-semibold uppercase tracking-wide',
            status === 'pending' ? 'text-steel-500' : 'text-steel-100'
          )}
        >
          {name}
        </span>
        <span
          className={clsx(
            'font-mono text-[10px] uppercase tracking-wider',
            status === 'running' && 'text-ember',
            status === 'completed' && 'text-ok',
            status === 'failed' && 'text-danger',
            (status === 'pending' || status === 'cancelled') && 'text-steel-600'
          )}
        >
          {statusLabel}
        </span>
      </div>

      {entries.length > 0 && (
        <dl className="mt-1.5 flex flex-wrap gap-x-4 gap-y-0.5">
          {entries.map(([key, value]) => (
            <div key={key} className="flex items-baseline gap-1.5">
              <dd className="font-mono text-sm font-semibold text-ember-400">{value}</dd>
              <dt className="text-[11px] text-steel-400">{labels.countLabel(key)}</dt>
            </div>
          ))}
        </dl>
      )}
    </div>
  );
}

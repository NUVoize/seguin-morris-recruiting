'use client';

import {useEffect, useRef, useState} from 'react';
import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/navigation';
import {ApiError, agentRuns} from '@/lib/api';
import type {AgentRun, AgentType} from '@/lib/api';
import {AGENT_ICONS, IconArrowRight, IconBolt} from '@/components/icons';
import {StationRail} from './StationRail';
import {Console} from './Console';
import {Tally} from './Tally';

type Phase = 'idle' | 'running' | 'completed' | 'failed';

const AGENT_ORDER: AgentType[] = [
  'employment_source',
  'school_pipeline',
  'lead_enrichment',
  'candidate_vetting',
  'fit_ranking'
];

const COUNT_KEYS = [
  'candidates_created',
  'sources_visited',
  'schools_contacted',
  'candidates_enriched',
  'qualifications_added',
  'scored',
  'strong_matches'
] as const;

/**
 * The live agent theater — an operations console.
 *
 * Polling strategy (unchanged from the working implementation):
 *   - Trigger returns `started_at` (the moment FastAPI accepted the request).
 *   - Poll `/api/agent-runs?since=<started_at>&limit=20` every 800ms.
 *   - Stop when fit_ranking reports status === 'completed'.
 *   - Tolerate transient HTTP failures (mid-INSERT races are normal).
 */
export function AgentTheater() {
  const t = useTranslations('run');
  const tAgents = useTranslations('run.agents');
  const tStatus = useTranslations('run.status');
  const tCounts = useTranslations('run.counts');

  const [phase, setPhase] = useState<Phase>('idle');
  const [triggerTime, setTriggerTime] = useState<string | null>(null);
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [triggerError, setTriggerError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function handleLaunch() {
    setTriggerError(null);
    setRuns([]);
    setElapsed(0);
    setPhase('running');
    try {
      const resp = await agentRuns.trigger();
      setTriggerTime(resp.started_at);
    } catch (err) {
      const message =
        err instanceof ApiError ? `${err.status} \u2014 ${err.message}` : (err as Error).message;
      setTriggerError(message);
      setPhase('failed');
    }
  }

  // Poll while running (logic unchanged).
  useEffect(() => {
    if (phase !== 'running' || !triggerTime) return;

    let cancelled = false;
    let consecutiveErrors = 0;

    async function pollOnce() {
      try {
        if (!triggerTime) return;
        const fresh = await agentRuns.list({since: triggerTime, limit: 20});
        if (cancelled) return;
        setRuns(fresh);
        consecutiveErrors = 0;

        const fit = fresh.find((r) => r.agent_type === 'fit_ranking');
        if (fit && fit.status === 'completed') {
          stop();
          setPhase('completed');
        } else if (fit && fit.status === 'failed') {
          stop();
          setPhase('failed');
          setTriggerError(t('errors.agent_failed'));
        }
      } catch {
        consecutiveErrors += 1;
        if (consecutiveErrors > 8) {
          stop();
          setPhase('failed');
          setTriggerError(t('errors.poll_failed'));
        }
      }
    }

    function stop() {
      cancelled = true;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    void pollOnce();
    intervalRef.current = setInterval(pollOnce, 800);
    return stop;
  }, [phase, triggerTime, t]);

  // Elapsed-time clock while running.
  useEffect(() => {
    if (phase !== 'running') return;
    const id = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(id);
  }, [phase]);

  const countLabel = (key: string) =>
    (COUNT_KEYS as readonly string[]).includes(key)
      ? tCounts(key as (typeof COUNT_KEYS)[number])
      : key.replace(/_/g, ' ');

  // ----------------------------------- idle: launch pad

  if (phase === 'idle') {
    return (
      <section className="bg-navy-950 text-steel-100">
        <div className="mx-auto flex min-h-[calc(100vh-7.5rem)] max-w-5xl flex-col items-center justify-center px-6 py-20 text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-ember">
            {t('eyebrow')}
          </p>
          <h1 className="mt-5 font-display text-5xl font-bold uppercase tracking-tight sm:text-6xl">
            {t('title')}
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-relaxed text-steel-300">
            {t('subtitle')}
          </p>

          <button
            type="button"
            onClick={handleLaunch}
            className="group mt-10 inline-flex items-center gap-2.5 rounded-lg bg-ember px-8 py-3.5 font-display text-lg font-semibold uppercase tracking-wide text-white shadow-lg shadow-ember/25 transition hover:bg-ember-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-ember focus-visible:ring-offset-2 focus-visible:ring-offset-navy-950"
          >
            <IconBolt size={18} />
            {t('launch_button')}
          </button>

          {/* Horizontal preview of the pipeline with a traveling flow dot */}
          <div className="relative mt-16 w-full max-w-3xl">
            <div className="absolute left-8 right-8 top-[18px] h-px overflow-hidden bg-steel-800" aria-hidden>
              <span
                className="sm-flow-dot absolute top-1/2 h-1 w-10 -translate-y-1/2 rounded-full bg-gradient-to-r from-transparent via-ember to-transparent"
                style={{['--sm-flow-distance' as never]: 'min(620px, 80vw)'}}
              />
            </div>
            <ol className="relative grid grid-cols-5 gap-2">
              {AGENT_ORDER.map((agent) => {
                const Icon = AGENT_ICONS[agent];
                return (
                  <li key={agent} className="flex flex-col items-center gap-2.5">
                    <span className="flex h-9 w-9 items-center justify-center rounded-full border border-steel-700 bg-navy-950 text-steel-300">
                      {Icon && <Icon size={15} />}
                    </span>
                    <span className="font-display text-xs font-semibold uppercase tracking-wide text-steel-400">
                      {tAgents(agent)}
                    </span>
                  </li>
                );
              })}
            </ol>
          </div>

          <p className="mt-14 max-w-md font-mono text-[10px] leading-relaxed text-steel-600">
            {t('vetting_reminder')}
          </p>
        </div>
      </section>
    );
  }

  // ----------------------------------- running / completed / failed

  const runsByType = new Map(runs.map((r) => [r.agent_type, r]));
  const discoveredCount = runs
    .filter((r) => r.agent_type === 'employment_source' || r.agent_type === 'school_pipeline')
    .reduce((acc, r) => acc + (r.output?.counts?.candidates_created ?? 0), 0);
  const fitRun = runsByType.get('fit_ranking');
  const scoredCount = fitRun?.output?.counts?.scored ?? 0;
  const strongCount = fitRun?.output?.counts?.strong_matches ?? 0;
  const allDone = phase === 'completed';
  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const ss = String(elapsed % 60).padStart(2, '0');

  return (
    <section className="flex flex-1 flex-col bg-navy-950 text-steel-100">
      <div className="mx-auto flex w-full max-w-7xl flex-1 flex-col px-4 py-8 sm:px-6">
        <header className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-ember">
              {t('eyebrow')}
            </p>
            <h1 className="mt-1.5 font-display text-3xl font-bold uppercase tracking-tight sm:text-4xl">
              {allDone ? t('header.done') : t('header.live')}
            </h1>
          </div>
          {phase === 'running' && (
            <div className="flex items-center gap-3 font-mono text-sm tabular-nums text-steel-400">
              <span className="sm-blink h-2 w-2 rounded-full bg-ember" aria-hidden />
              {mm}:{ss}
            </div>
          )}
          {allDone && (
            <p className="font-mono text-sm text-steel-400">
              {t('discovered_count', {count: discoveredCount})}
            </p>
          )}
        </header>

        {allDone && (
          <div className="mt-6">
            <Tally
              stats={[
                {key: 'disc', label: t('tally.discovered'), value: discoveredCount},
                {key: 'scored', label: t('tally.scored'), value: scoredCount},
                {key: 'strong', label: t('tally.strong'), value: strongCount, accent: true}
              ]}
            />
          </div>
        )}

        <div className="mt-6 grid min-h-0 flex-1 gap-5 lg:grid-cols-[300px_1fr]">
          <StationRail
            order={AGENT_ORDER}
            runsByType={runsByType}
            agentName={(a) => tAgents(a)}
            labels={{
              pending: tStatus('pending'),
              running: tStatus('running'),
              completed: tStatus('completed'),
              failed: tStatus('failed'),
              countLabel
            }}
          />
          <div className="min-h-[420px] lg:min-h-0">
            <Console
              order={AGENT_ORDER}
              runsByType={runsByType}
              waitingLabel={tStatus('waiting')}
              titleLabel={t('console_title')}
              live={phase === 'running'}
            />
          </div>
        </div>

        {(phase === 'completed' || phase === 'failed') && (
          <div className="sm-rise mt-7 flex flex-col items-center gap-3 text-center">
            {phase === 'completed' ? (
              <>
                <p className="text-sm text-steel-400">{t('cta.done_subtitle')}</p>
                <Link
                  href="/candidates"
                  className="inline-flex items-center gap-2.5 rounded-lg bg-ember px-7 py-3 font-display text-base font-semibold uppercase tracking-wide text-white shadow-lg shadow-ember/25 transition hover:bg-ember-600"
                >
                  {t('cta.view_pipeline')}
                  <IconArrowRight size={16} />
                </Link>
                <button
                  type="button"
                  onClick={handleLaunch}
                  className="text-xs text-steel-500 underline-offset-2 transition hover:text-steel-300 hover:underline"
                >
                  {t('cta.run_again')}
                </button>
              </>
            ) : (
              <>
                <p className="font-display text-base font-semibold uppercase tracking-wide text-danger">
                  {t('errors.title')}
                </p>
                {triggerError && (
                  <p className="font-mono text-xs text-danger/80">{triggerError}</p>
                )}
                <button
                  type="button"
                  onClick={handleLaunch}
                  className="mt-1 inline-flex items-center gap-2 rounded-lg bg-steel-100 px-6 py-2.5 font-display text-sm font-semibold uppercase tracking-wide text-navy-950 transition hover:bg-white"
                >
                  {t('cta.retry')}
                </button>
              </>
            )}
          </div>
        )}

        <p className="mt-8 text-center font-mono text-[10px] text-steel-600">
          {t('vetting_reminder')}
        </p>
      </div>
    </section>
  );
}

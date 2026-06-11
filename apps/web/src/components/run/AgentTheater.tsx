'use client';

import {useEffect, useRef, useState} from 'react';
import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/navigation';
import {ApiError, agentRuns} from '@/lib/api';
import type {AgentRun, AgentType} from '@/lib/api';
import {AgentCard} from './AgentCard';

type Phase = 'idle' | 'running' | 'completed' | 'failed';

const AGENT_ORDER: AgentType[] = [
  'employment_source',
  'school_pipeline',
  'lead_enrichment',
  'candidate_vetting',
  'fit_ranking'
];

// Use Unicode escapes so the file is ASCII-safe regardless of editor/encoding.
const AGENT_ICONS: Record<AgentType, string> = {
  employment_source: '\u{1F50D}',  // magnifying glass
  school_pipeline: '\u{1F393}',    // graduation cap
  lead_enrichment: '\u{1F9F9}',    // broom
  candidate_vetting: '\u{1F6E1}',  // shield
  fit_ranking: '\u{1F3AF}',        // target
  event_discovery: '\u{1F4C5}',    // calendar
  outreach: '\u{2709}\u{FE0F}',    // envelope
  email_sync: '\u{1F4E7}',         // email
  assistant_knowledge: '\u{1F4AC}',// speech bubble
  reporting: '\u{1F4CA}'           // bar chart
};

/**
 * The live agent theater. Click the big button, watch 5 agents do their work,
 * land on a "view pipeline" CTA at the end.
 *
 * Polling strategy:
 *   - Trigger returns `started_at` (the moment FastAPI accepted the request).
 *   - We poll `/api/agent-runs?since=<started_at>&limit=20` every 800ms.
 *   - When the fit_ranking agent reports status === 'completed', stop polling.
 *   - On any HTTP failure, surface it but keep polling for a few rounds â€”
 *     mid-INSERT races are normal during a run.
 */
export function AgentTheater() {
  const t = useTranslations('run');
  const tAgents = useTranslations('run.agents');
  const tStatus = useTranslations('run.status');

  const [phase, setPhase] = useState<Phase>('idle');
  const [triggerTime, setTriggerTime] = useState<string | null>(null);
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [triggerError, setTriggerError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function handleLaunch() {
    setTriggerError(null);
    setRuns([]);
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

  // Poll while running.
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

  // ----------------------------------- render

  if (phase === 'idle') {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16 text-center">
        <p className="text-xs uppercase tracking-widest text-neutral-500">{t('eyebrow')}</p>
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900 sm:text-4xl">
          {t('title')}
        </h1>
        <p className="mt-4 text-base leading-relaxed text-neutral-600">{t('subtitle')}</p>

        <button
          type="button"
          onClick={handleLaunch}
          className="mt-10 inline-flex items-center gap-2 rounded-lg bg-neutral-900 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-neutral-700 focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:ring-offset-2"
        >
          {t('launch_button')}
        </button>

        <div className="mt-12 grid grid-cols-1 gap-3 text-left sm:grid-cols-5">
          {AGENT_ORDER.map((agent) => (
            <div
              key={agent}
              className="rounded-lg border border-dashed border-neutral-200 bg-white p-3"
            >
              <div className="text-xl" aria-hidden>
                {AGENT_ICONS[agent]}
              </div>
              <div className="mt-2 text-xs font-medium text-neutral-700">{tAgents(agent)}</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const runsByType = new Map(runs.map((r) => [r.agent_type, r]));
  const discoveredCount = runs
    .filter((r) => r.agent_type === 'employment_source' || r.agent_type === 'school_pipeline')
    .reduce((acc, r) => acc + (r.output?.counts?.candidates_created ?? 0), 0);
  const allDone = phase === 'completed';

  return (
    <div className="mx-auto max-w-7xl px-6 py-10">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-widest text-neutral-500">{t('eyebrow')}</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-neutral-900 sm:text-3xl">
            {allDone ? t('header.done') : t('header.live')}
          </h1>
        </div>

        {allDone && (
          <div className="flex items-center gap-2 text-sm text-neutral-600">
            <span>{t('discovered_count', {count: discoveredCount})}</span>
          </div>
        )}
      </header>

      <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-5">
        {AGENT_ORDER.map((agent) => (
          <AgentCard
            key={agent}
            agentType={agent}
            displayName={tAgents(agent)}
            icon={AGENT_ICONS[agent]}
            run={runsByType.get(agent) ?? null}
            labels={{
              pending: tStatus('pending'),
              running: tStatus('running'),
              completed: tStatus('completed'),
              failed: tStatus('failed'),
              waiting: tStatus('waiting')
            }}
          />
        ))}
      </div>

      {(phase === 'completed' || phase === 'failed') && (
        <div className="mt-10 flex flex-col items-center gap-3 rounded-lg border border-neutral-200 bg-neutral-50 p-6 text-center">
          {phase === 'completed' ? (
            <>
              <p className="text-sm text-neutral-700">{t('cta.done_subtitle')}</p>
              <Link
                href="/candidates"
                className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-emerald-700"
              >
                {t('cta.view_pipeline')}
              </Link>
              <button
                type="button"
                onClick={handleLaunch}
                className="text-xs text-neutral-500 underline-offset-2 hover:underline"
              >
                {t('cta.run_again')}
              </button>
            </>
          ) : (
            <>
              <p className="text-sm font-medium text-red-700">{t('errors.title')}</p>
              {triggerError && (
                <p className="font-mono text-xs text-red-600">{triggerError}</p>
              )}
              <button
                type="button"
                onClick={handleLaunch}
                className="mt-2 inline-flex items-center gap-2 rounded-lg bg-neutral-900 px-5 py-2.5 text-sm font-medium text-white"
              >
                {t('cta.retry')}
              </button>
            </>
          )}
        </div>
      )}

      <p className="mt-8 text-center text-xs text-neutral-400">{t('vetting_reminder')}</p>
    </div>
  );
}
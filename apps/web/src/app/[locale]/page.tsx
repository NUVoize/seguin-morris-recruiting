import {getTranslations, setRequestLocale} from 'next-intl/server';
import {Link} from '@/i18n/navigation';
import {
  AGENT_ICONS,
  IconArrowRight,
  IconBolt,
  IconRadar,
  IconShield,
  IconTarget
} from '@/components/icons';
import type {AgentType} from '@/lib/api';

const PIPELINE_PREVIEW: AgentType[] = [
  'employment_source',
  'school_pipeline',
  'lead_enrichment',
  'candidate_vetting',
  'fit_ranking'
];

/**
 * Landing: navy hero stating what the product does, an animated diagram of
 * the agent pipeline, and three capability blocks grounded in the Quebec
 * refrigeration domain (sources, compliance vetting, advisory scoring).
 */
export default async function HomePage({
  params
}: {
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  setRequestLocale(locale);

  const tHome = await getTranslations('home');
  const tAgents = await getTranslations('run.agents');

  const features = [
    {key: 'sources', icon: IconRadar},
    {key: 'vetting', icon: IconShield},
    {key: 'scoring', icon: IconTarget}
  ] as const;

  return (
    <main className="flex flex-1 flex-col">
      {/* Hero */}
      <section className="bg-navy-950 text-white">
        <div className="mx-auto max-w-6xl px-6 pb-16 pt-16 sm:pb-20 sm:pt-20">
          <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-ember">
            {tHome('eyebrow')}
          </p>
          <h1 className="mt-5 max-w-3xl font-display text-5xl font-bold uppercase leading-[0.95] tracking-tight sm:text-7xl">
            {tHome('hero_line1')}
            <span className="block text-ember">{tHome('hero_line2')}</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-steel-300">
            {tHome('subtitle')}
          </p>

          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/run"
              className="inline-flex items-center justify-center gap-2.5 rounded-lg bg-ember px-7 py-3.5 font-display text-lg font-semibold uppercase tracking-wide text-white shadow-lg shadow-ember/25 transition hover:bg-ember-600"
            >
              <IconBolt size={18} />
              {tHome('launch_agents')}
            </Link>
            <Link
              href="/candidates"
              className="inline-flex items-center justify-center gap-2.5 rounded-lg border border-steel-600 px-7 py-3.5 font-display text-lg font-semibold uppercase tracking-wide text-steel-200 transition hover:border-steel-400 hover:text-white"
            >
              {tHome('open_pipeline')}
              <IconArrowRight size={16} />
            </Link>
          </div>

          {/* Animated pipeline diagram */}
          <div className="relative mt-16 max-w-3xl">
            <div
              className="absolute left-7 right-7 top-[18px] hidden h-px overflow-hidden bg-steel-800 sm:block"
              aria-hidden
            >
              <span
                className="sm-flow-dot absolute top-1/2 h-1 w-10 -translate-y-1/2 rounded-full bg-gradient-to-r from-transparent via-ember to-transparent"
                style={{['--sm-flow-distance' as never]: 'min(620px, 76vw)'}}
              />
            </div>
            <ol className="relative grid grid-cols-2 gap-x-2 gap-y-6 sm:grid-cols-5">
              {PIPELINE_PREVIEW.map((agent) => {
                const Icon = AGENT_ICONS[agent];
                return (
                  <li key={agent} className="flex flex-col items-center gap-2.5 text-center">
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
        </div>
      </section>

      {/* Capability blocks — grounded in the Quebec refrigeration domain */}
      <section className="mx-auto w-full max-w-6xl px-6 py-14 sm:py-16">
        <div className="grid gap-5 sm:grid-cols-3">
          {features.map(({key, icon: Icon}) => (
            <article
              key={key}
              className="rounded-xl border border-steel-100 bg-white p-6 shadow-sm"
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-navy/8 text-navy">
                <Icon size={18} />
              </span>
              <h2 className="mt-4 font-display text-xl font-bold uppercase tracking-wide text-steel-900">
                {tHome(`features.${key}.title`)}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-steel-500">
                {tHome(`features.${key}.body`)}
              </p>
            </article>
          ))}
        </div>

        <p className="mt-10 text-center font-mono text-[10px] leading-relaxed text-steel-400">
          {tHome('advisory_note')}
        </p>
      </section>
    </main>
  );
}

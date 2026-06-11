import Image from 'next/image';
import {getTranslations, setRequestLocale} from 'next-intl/server';
import {Suspense} from 'react';

import {LoginForm} from '@/components/auth/LoginForm';
import {AGENT_ICONS} from '@/components/icons';
import type {AgentType} from '@/lib/api';

const PIPELINE: AgentType[] = [
  'employment_source',
  'school_pipeline',
  'lead_enrichment',
  'candidate_vetting',
  'fit_ranking'
];

export default async function LoginPage({params}: {params: Promise<{locale: string}>}) {
  const {locale} = await params;
  setRequestLocale(locale);
  const t = await getTranslations('login');
  const tAgents = await getTranslations('run.agents');

  return (
    <main className="grid flex-1 lg:grid-cols-[1.1fr_1fr]">
      {/* Brand panel */}
      <section className="hidden flex-col justify-between bg-navy-950 p-10 text-white lg:flex">
        <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-ember">
          {t('eyebrow')}
        </p>
        <div>
          <h1 className="max-w-md font-display text-5xl font-bold uppercase leading-[0.95] tracking-tight">
            {t('brand_line1')}
            <span className="block text-ember">{t('brand_line2')}</span>
          </h1>
          <ul className="mt-10 flex items-center gap-5">
            {PIPELINE.map((a) => {
              const Icon = AGENT_ICONS[a];
              return (
                <li key={a} title={tAgents(a)}>
                  <span className="flex h-9 w-9 items-center justify-center rounded-full border border-steel-700 text-steel-400">
                    {Icon && <Icon size={15} />}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
        <p className="font-mono text-[10px] uppercase tracking-wider text-steel-600">
          {t('designed_by')}
        </p>
      </section>

      {/* Form panel */}
      <section className="flex items-center justify-center bg-steel-0 px-6 py-14">
        <div className="w-full max-w-sm">
          <Image
            src="/brand-seguin-morris.png"
            alt="Seguin Morris"
            width={397}
            height={159}
            priority
            className="h-12 w-auto"
          />
          <h2 className="mt-8 font-display text-2xl font-bold uppercase tracking-tight text-steel-900">
            {t('title')}
          </h2>
          <p className="mt-1 text-sm text-steel-500">{t('subtitle')}</p>
          <Suspense>
            <LoginForm />
          </Suspense>
        </div>
      </section>
    </main>
  );
}

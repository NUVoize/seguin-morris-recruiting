import {setRequestLocale} from 'next-intl/server';
import {cookies} from 'next/headers';
import {Suspense} from 'react';

import {apiRequest, type Candidate} from '@/lib/api';

import {KanbanBoard} from '@/components/pipeline/KanbanBoard';

interface Props {
  params: Promise<{locale: string}>;
}

export default async function CandidatesPage({params}: Props) {
  const {locale} = await params;
  setRequestLocale(locale);
  const token = (await cookies()).get('sm_session')?.value ?? null;

  // Server-side fetch — runs at request time, no cache (no-store via client default).
  let initial: Candidate[] = [];
  let fetchError: string | null = null;

  try {
    initial = await apiRequest<Candidate[]>('/candidates', {query: {limit: 200}, token});
  } catch (err) {
    fetchError = err instanceof Error ? err.message : 'Unknown error';
  }

  if (fetchError) {
    return (
      <main className="flex flex-1 items-center justify-center p-6">
        <div className="max-w-md rounded-xl border border-danger/30 bg-danger-soft p-6 text-center">
          <h2 className="font-display text-lg font-bold uppercase tracking-wide text-danger">
            Backend unreachable
          </h2>
          <p className="mt-2 text-sm text-steel-700">{fetchError}</p>
          <p className="mt-3 text-xs text-steel-500">
            Start the API with{' '}
            <code className="rounded bg-white px-1 py-0.5 font-mono">uvicorn app.main:app --reload --port 8000</code>{' '}
            and refresh.
          </p>
        </div>
      </main>
    );
  }

  return (
    <Suspense>
      <KanbanBoard initialCandidates={initial} />
    </Suspense>
  );
}

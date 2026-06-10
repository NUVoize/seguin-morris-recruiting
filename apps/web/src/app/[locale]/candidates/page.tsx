import {setRequestLocale} from 'next-intl/server';
import {Suspense} from 'react';

import {apiRequest, type Candidate} from '@/lib/api';

import {KanbanBoard} from '@/components/pipeline/KanbanBoard';

interface Props {
  params: Promise<{locale: string}>;
}

export default async function CandidatesPage({params}: Props) {
  const {locale} = await params;
  setRequestLocale(locale);

  // Server-side fetch — runs at request time, no cache (no-store via client default).
  let initial: Candidate[] = [];
  let fetchError: string | null = null;

  try {
    initial = await apiRequest<Candidate[]>('/candidates', {query: {limit: 200}});
  } catch (err) {
    fetchError = err instanceof Error ? err.message : 'Unknown error';
  }

  if (fetchError) {
    return (
      <main className="flex flex-1 items-center justify-center p-6">
        <div className="max-w-md rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <h2 className="text-lg font-semibold text-red-900">Backend unreachable</h2>
          <p className="mt-2 text-sm text-red-800">{fetchError}</p>
          <p className="mt-3 text-xs text-red-700">
            Start the API with{' '}
            <code className="rounded bg-white px-1 py-0.5">uvicorn app.main:app --reload --port 8000</code>{' '}
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

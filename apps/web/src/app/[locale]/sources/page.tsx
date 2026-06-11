import {setRequestLocale} from 'next-intl/server';
import {cookies} from 'next/headers';

import {apiRequest, type LeadSource} from '@/lib/api';
import {SourceDirectory} from '@/components/sources/SourceDirectory';

interface Props {
  params: Promise<{locale: string}>;
}

export default async function SourcesPage({params}: Props) {
  const {locale} = await params;
  setRequestLocale(locale);
  const token = (await cookies()).get('sm_session')?.value ?? null;

  let initial: LeadSource[] = [];
  let fetchError: string | null = null;
  try {
    initial = await apiRequest<LeadSource[]>('/sources', {query: {limit: 100}, token});
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
        </div>
      </main>
    );
  }

  return <SourceDirectory initialSources={initial} />;
}

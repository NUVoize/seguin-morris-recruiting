import {setRequestLocale} from 'next-intl/server';
import {AgentTheater} from '@/components/run/AgentTheater';

export default async function RunPage({
  params
}: {
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  setRequestLocale(locale);
  return (
    <main className="min-h-[calc(100vh-4rem)] bg-neutral-50">
      <AgentTheater />
    </main>
  );
}

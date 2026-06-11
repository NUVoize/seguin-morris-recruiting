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
    <main className="flex flex-1 flex-col">
      <AgentTheater />
    </main>
  );
}

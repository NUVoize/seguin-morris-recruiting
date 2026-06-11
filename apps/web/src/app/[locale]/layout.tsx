import type {Metadata} from 'next';
import {Barlow, Barlow_Condensed, IBM_Plex_Mono} from 'next/font/google';
import {NextIntlClientProvider} from 'next-intl';
import {getMessages, getTranslations, setRequestLocale} from 'next-intl/server';
import {notFound} from 'next/navigation';
import {routing} from '@/i18n/routing';
import {AppShell} from '@/components/layout/AppShell';
import '../globals.css';

const barlow = Barlow({
  variable: '--font-barlow',
  weight: ['400', '500', '600', '700'],
  subsets: ['latin']
});

const barlowCondensed = Barlow_Condensed({
  variable: '--font-barlow-condensed',
  weight: ['500', '600', '700'],
  style: ['normal', 'italic'],
  subsets: ['latin']
});

const plexMono = IBM_Plex_Mono({
  variable: '--font-plex-mono',
  weight: ['400', '500', '600'],
  subsets: ['latin']
});

export function generateStaticParams() {
  return routing.locales.map((locale) => ({locale}));
}

export async function generateMetadata({
  params
}: {
  params: Promise<{locale: string}>;
}): Promise<Metadata> {
  const {locale} = await params;
  const t = await getTranslations({locale, namespace: 'brand'});
  return {
    title: `${t('company')} — ${t('tagline')}`,
    description: t('designed_by')
  };
}

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;

  if (!routing.locales.includes(locale as (typeof routing.locales)[number])) {
    notFound();
  }

  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    <html
      lang={locale}
      className={`${barlow.variable} ${barlowCondensed.variable} ${plexMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-steel-0 text-steel-900">
        <NextIntlClientProvider messages={messages}>
          <AppShell>{children}</AppShell>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

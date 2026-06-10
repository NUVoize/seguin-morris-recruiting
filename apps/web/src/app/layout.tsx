/**
 * Root layout — required by Next.js but does almost nothing.
 * The real layout (fonts, html lang, NextIntlClientProvider) lives at
 * src/app/[locale]/layout.tsx so it can read the current locale.
 *
 * The middleware redirects "/" -> "/fr" (or "/en") before this is rendered
 * with real content; this exists mainly to satisfy Next.js's requirement.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}

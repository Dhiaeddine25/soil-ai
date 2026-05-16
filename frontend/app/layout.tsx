import type { Metadata } from 'next';
import { Sora } from 'next/font/google';

import { AuthProvider } from '@/components/auth/auth-provider';
import { SiteShell } from '@/components/layout/site-shell';
import { I18nProvider } from '@/components/i18n/i18n-provider';
import 'leaflet/dist/leaflet.css';
import './globals.css';

export const metadata: Metadata = {
  title: 'SoilAI',
  description: 'Private agritech workspace for parcel analysis, history, and reports.',
};

const sora = Sora({ subsets: ['latin'], display: 'swap', variable: '--font-sora' });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" dir="ltr" suppressHydrationWarning>
      <body className={`${sora.variable} min-h-screen bg-background text-foreground antialiased`}>
        <I18nProvider>
          <AuthProvider>
            <SiteShell>{children}</SiteShell>
          </AuthProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
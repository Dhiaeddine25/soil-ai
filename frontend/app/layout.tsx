import type { Metadata } from 'next';

import { AuthProvider } from '@/components/auth/auth-provider';
import { SiteShell } from '@/components/layout/site-shell';
import { I18nProvider } from '@/components/i18n/i18n-provider';
import 'leaflet/dist/leaflet.css';
import './globals.css';

export const metadata: Metadata = {
  title: 'SoilAI',
  description: 'Private agritech workspace for parcel analysis, history, and reports.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" dir="ltr" suppressHydrationWarning>
      <body>
        <I18nProvider>
          <AuthProvider>
            <SiteShell>{children}</SiteShell>
          </AuthProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
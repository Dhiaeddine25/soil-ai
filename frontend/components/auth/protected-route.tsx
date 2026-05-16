"use client";

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, Sparkles } from 'lucide-react';

import { Card } from '@/components/ui/card';
import { useAuth } from './auth-provider';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, loading, status, error, refresh } = useAuth();
  const [timedOut, setTimedOut] = useState(false);
  const [retrying, setRetrying] = useState(false);

  const showError = status === 'error' || timedOut;
  const errorMessage = error ?? 'Le serveur est temporairement inaccessible.';

  useEffect(() => {
    if (!loading) {
      setTimedOut(false);
      return;
    }

    const timeoutId = setTimeout(() => setTimedOut(true), 8000);
    return () => clearTimeout(timeoutId);
  }, [loading]);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isAuthenticated, loading, router]);

  const skeletonBlocks = useMemo(() => Array.from({ length: 3 }), []);

  if (loading && !timedOut) {
    return (
      <div className="relative min-h-[70vh] overflow-hidden px-4 py-16 sm:px-6 lg:px-8">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(115,140,89,0.16),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(180,138,71,0.12),_transparent_28%),linear-gradient(180deg,_#faf7f0_0%,_#f4efe4_55%,_#ece5d8_100%)]" />
        <div className="pointer-events-none absolute left-[-5rem] top-16 h-64 w-64 rounded-full bg-leaf-200/30 blur-3xl" />
        <div className="pointer-events-none absolute right-[-6rem] top-8 h-72 w-72 rounded-full bg-amber-200/25 blur-3xl" />

        <div className="relative mx-auto max-w-5xl">
          <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
            <Card className="space-y-5 border-white/70 bg-white/85 p-6 shadow-[0_24px_80px_rgba(68,64,60,0.16)] backdrop-blur-xl sm:p-8">
              <div className="inline-flex items-center gap-2 rounded-full border border-leaf-200 bg-leaf-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-leaf-700">
                <ShieldCheck className="h-4 w-4" />
                Session
              </div>
              <div className="space-y-2">
                <div className="text-3xl font-semibold tracking-tight text-soil-950">Verification de la session en cours...</div>
                <p className="max-w-2xl text-sm leading-6 text-soil-600">
                  Nous vérifions votre accès pour afficher vos parcelles, analyses et résultats.
                </p>
              </div>
              <div className="flex items-center gap-3 rounded-2xl border border-soil-200 bg-white/80 px-4 py-3 text-sm text-soil-700">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-soil-300 border-t-transparent" />
                Connexion sécurisée en cours...
              </div>
            </Card>

            <div className="grid gap-3 sm:grid-cols-2">
              {skeletonBlocks.map((_, index) => (
                <Card key={`skeleton-${index}`} className="space-y-4 border-white/70 bg-white/75 p-5 shadow-soft backdrop-blur">
                  <div className="flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-soil-900 text-white">
                      <Sparkles className="h-4 w-4" />
                    </span>
                    <div>
                      <div className="h-4 w-24 rounded-full bg-soil-100" />
                      <div className="mt-2 h-3 w-32 rounded-full bg-soil-100" />
                    </div>
                  </div>
                  <div className="h-4 w-2/3 rounded-full bg-soil-100" />
                  <div className="h-3 w-full rounded-full bg-soil-100" />
                  <div className="h-3 w-5/6 rounded-full bg-soil-100" />
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (showError && !isAuthenticated) {
    return (
      <div className="px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-xl">
          <Card className="space-y-4 border-amber-200 bg-amber-50 text-amber-900">
            <div className="text-lg font-semibold">Connexion impossible</div>
            <p className="text-sm">{errorMessage}</p>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                className="rounded-full bg-soil-900 px-4 py-2 text-sm font-semibold text-white"
                onClick={async () => {
                  setRetrying(true);
                  setTimedOut(false);
                  try {
                    await refresh();
                  } finally {
                    setRetrying(false);
                  }
                }}
                disabled={retrying}
              >
                {retrying ? 'Reessai...' : 'Reessayer'}
              </button>
              <button
                type="button"
                className="rounded-full border border-soil-200 bg-white px-4 py-2 text-sm font-semibold text-soil-700"
                onClick={() => router.replace('/')}
              >
                Retour accueil
              </button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
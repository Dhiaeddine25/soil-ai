"use client";

import Link from 'next/link';
import { ArrowRight, ScanSearch, ShieldCheck, Sprout } from 'lucide-react';

import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';

export function AuthShell({ children, variant = 'login' }: { children: React.ReactNode; variant?: 'login' | 'register' }) {
  const { messages } = useI18n();
  const title = variant === 'register' ? messages.auth.registerTitle : messages.auth.loginTitle;
  const subtitle = variant === 'register' ? messages.auth.registerSubtitle : messages.auth.loginSubtitle;

  return (
    <div className="relative overflow-hidden px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,_rgba(115,140,89,0.18),_transparent_32%),radial-gradient(circle_at_bottom_right,_rgba(121,92,46,0.14),_transparent_28%),linear-gradient(180deg,_#faf7f0_0%,_#f3efe4_55%,_#ebe4d7_100%)]" />
      <div className="pointer-events-none absolute left-[-6rem] top-24 -z-10 h-72 w-72 rounded-full bg-leaf-200/30 blur-3xl" />
      <div className="pointer-events-none absolute right-[-5rem] top-8 -z-10 h-80 w-80 rounded-full bg-amber-200/25 blur-3xl" />

      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-leaf-200 bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-leaf-700 shadow-sm backdrop-blur">
            <Sprout className="h-4 w-4" />
            {messages.shell.appTagline}
          </div>

          <div className="space-y-4">
            <h1 className="max-w-xl text-4xl font-semibold tracking-tight text-soil-950 sm:text-5xl">{title}</h1>
            <p className="max-w-2xl text-base leading-7 text-soil-700 sm:text-lg">{subtitle}</p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-3xl border border-white/70 bg-white/80 p-4 shadow-soft backdrop-blur">
              <ShieldCheck className="h-5 w-5 text-leaf-700" />
              <div className="mt-3 text-sm font-semibold text-soil-900">Accès sécurisé</div>
              <div className="mt-1 text-xs leading-5 text-soil-600">Compte protégé et session privée pour chaque utilisateur.</div>
            </div>
            <div className="rounded-3xl border border-white/70 bg-white/80 p-4 shadow-soft backdrop-blur">
              <ScanSearch className="h-5 w-5 text-soil-700" />
              <div className="mt-3 text-sm font-semibold text-soil-900">Analyse rapide</div>
              <div className="mt-1 text-xs leading-5 text-soil-600">Importez une image et lancez l’analyse en quelques secondes.</div>
            </div>
            <div className="rounded-3xl border border-white/70 bg-white/80 p-4 shadow-soft backdrop-blur">
              <ArrowRight className="h-5 w-5 text-amber-700" />
              <div className="mt-3 text-sm font-semibold text-soil-900">Résultats lisibles</div>
              <div className="mt-1 text-xs leading-5 text-soil-600">Historique, conseils et score terrain centralisés.</div>
            </div>
          </div>

          <div className="text-sm text-soil-600">
            <Link href="/" className="inline-flex items-center gap-2 font-semibold text-leaf-700 hover:text-leaf-800">
              {messages.auth.backHome}
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-4 -z-10 rounded-[2rem] bg-white/35 blur-2xl" />
          <Card className="border-white/70 bg-white/85 p-6 shadow-[0_24px_80px_rgba(68,64,60,0.18)] backdrop-blur-xl sm:p-8">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-soil-900 text-white shadow-soft">
                <Sprout className="h-5 w-5" />
              </div>
              <div>
                <div className="text-xs uppercase tracking-[0.22em] text-soil-500">SoilAI</div>
                <div className="text-lg font-semibold text-soil-900">{variant === 'register' ? 'Créer un compte' : 'Se connecter'}</div>
              </div>
            </div>
            {children}
          </Card>
        </div>
      </div>
    </div>
  );
}
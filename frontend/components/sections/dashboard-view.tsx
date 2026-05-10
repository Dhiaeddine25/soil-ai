"use client";

import Link from 'next/link';
import { ArrowRight, CalendarDays, Leaf, MapPinned, TriangleAlert } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { getHistory, listParcels } from '@/lib/api';
import { useI18n } from '@/components/i18n/i18n-provider';
import { samplePrediction } from '@/lib/mock';
import type { HistoryEntry, ParcelPublic } from '@/lib/types';
import { buildWatchlist, getSoilScore } from '@/lib/soil-insights';

export function DashboardView() {
  const { user, token, loading } = useAuth();
  const { messages } = useI18n();
  const [historyEntries, setHistoryEntries] = useState<HistoryEntry[]>([]);
  const [parcels, setParcels] = useState<ParcelPublic[]>([]);

  const connectedLabel = loading ? '...' : (user?.full_name ?? user?.email ?? 'Session active');

  useEffect(() => {
    if (!user) {
      return;
    }

    const loadData = async () => {
      try {
        const [parcelItems, history] = await Promise.all([
          token ? listParcels(token) : Promise.resolve([]),
          token ? getHistory(user.id, token) : Promise.resolve({ user_id: user.id, total: 0, entries: [] }),
        ]);

        setParcels(parcelItems);
        setHistoryEntries(history.entries);
      } catch {
        setParcels([]);
        setHistoryEntries([]);
      }
    };

    void loadData();
  }, [token, user]);

  const watchlist = useMemo(() => buildWatchlist(historyEntries).slice(0, 4), [historyEntries]);
  const latestEntries = useMemo(() => [...historyEntries].sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()).slice(0, 3), [historyEntries]);
  const soilScores = historyEntries.map((entry) => getSoilScore(entry.prediction).score);
  const averageSoilScore = soilScores.length ? Math.round(soilScores.reduce((sum, value) => sum + value, 0) / soilScores.length) : getSoilScore(samplePrediction).score;
  const criticalCount = watchlist.filter((entry) => getSoilScore(entry.prediction).level === 'critique').length;
  const watchlistLabel = watchlist[0] ? getSoilScore(watchlist[0].prediction).focus : 'K';

  return (
    <section className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="grid gap-4 md:grid-cols-[1.2fr_0.8fr]">
          <Card className="space-y-4">
            <div className="text-sm uppercase tracking-[0.18em] text-soil-500">{messages.dashboard.title}</div>
            <div className="text-3xl font-semibold text-soil-900">{messages.dashboard.subtitle}</div>
            <div className="rounded-3xl border border-soil-200 bg-stone-50 p-4 text-sm text-soil-700">
              <div className="text-xs uppercase tracking-[0.18em] text-soil-500">{messages.dashboard.nextStep}</div>
              <div className="mt-2 font-medium text-soil-900">{connectedLabel}</div>
              <div className="mt-2 text-soil-600">{messages.dashboard.openAnalysis}</div>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/upload"><Button><Leaf className="h-4 w-4" />{messages.dashboard.openAnalysis}</Button></Link>
              <Link href="/history"><Button variant="ghost">{messages.dashboard.goToHistory}</Button></Link>
              <Link href="/parcels"><Button variant="ghost">{messages.dashboard.goToParcels}</Button></Link>
            </div>
          </Card>

          <Card className="space-y-3">
            <div className="text-sm uppercase tracking-[0.18em] text-soil-500">{messages.dashboard.quickActions}</div>
            <div className="space-y-2">
              {[
                { href: '/upload', icon: <Leaf className="h-4 w-4" />, label: messages.dashboard.openAnalysis },
                { href: '/parcels', icon: <MapPinned className="h-4 w-4" />, label: messages.dashboard.goToParcels },
                { href: '/history', icon: <CalendarDays className="h-4 w-4" />, label: messages.dashboard.goToHistory },
              ].map((item) => (
                <Link key={item.href} href={item.href} className="flex items-center justify-between rounded-2xl border border-soil-200 bg-white px-4 py-3 text-sm font-medium text-soil-700 hover:border-soil-300 hover:text-soil-900">
                  <span className="flex items-center gap-3">{item.icon}{item.label}</span>
                  <ArrowRight className="h-4 w-4 text-soil-400" />
                </Link>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <div className="text-sm text-soil-500">Analyses</div>
            <div className="mt-2 text-3xl font-semibold text-soil-900">{historyEntries.length}</div>
          </Card>
          <Card>
            <div className="text-sm text-soil-500">Parcelles</div>
            <div className="mt-2 text-3xl font-semibold text-soil-900">{parcels.length}</div>
          </Card>
          <Card>
            <div className="text-sm text-soil-500">Score sol moyen</div>
            <div className="mt-2 text-3xl font-semibold text-soil-900">{averageSoilScore}/100</div>
          </Card>
          <Card>
            <div className="text-sm text-soil-500">Parcelles à surveiller</div>
            <div className="mt-2 text-3xl font-semibold text-soil-900">{watchlist.length}</div>
          </Card>
        </div>

        <div className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
          <Card className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Parcelles à surveiller</div>
                <div className="mt-2 text-2xl font-semibold text-soil-900">Priorité {watchlistLabel} et derniers signaux faibles</div>
              </div>
              <TriangleAlert className="h-5 w-5 text-amber-500" />
            </div>

            <div className="space-y-3">
              {watchlist.length ? watchlist.map((entry) => {
                const soil = getSoilScore(entry.prediction);
                return (
                  <Link key={entry.analysis_id} href={`/history/${entry.analysis_id}`} className="block rounded-2xl border border-soil-200 bg-white p-4 transition hover:border-leaf-300 hover:shadow-sm">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="font-semibold text-soil-900">{entry.parcel?.name ?? entry.parcel_id ?? 'Parcelle inconnue'}</div>
                        <div className="text-sm text-soil-500">{new Date(entry.created_at).toLocaleString('fr-FR')}</div>
                      </div>
                      <div className={`rounded-full px-3 py-1 text-xs font-semibold ${soil.level === 'critique' ? 'bg-rose-100 text-rose-800' : soil.level === 'à surveiller' ? 'bg-amber-100 text-amber-800' : 'bg-sky-100 text-sky-800'}`}>
                        {soil.score}/100
                      </div>
                    </div>
                    <div className="mt-3 grid gap-2 sm:grid-cols-3">
                      <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">K {entry.prediction?.prediction?.K_level ?? '—'}</div>
                      <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">N {entry.prediction?.prediction?.N_level ?? '—'}</div>
                      <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">P {entry.prediction?.prediction?.P_level ?? '—'}</div>
                    </div>
                    <div className="mt-3 text-xs uppercase tracking-[0.18em] text-soil-500">{soil.status} · focus {soil.focus}</div>
                  </Link>
                );
              }) : (
                <div className="rounded-2xl border border-dashed border-soil-200 bg-stone-50 p-4 text-sm text-soil-600">
                  Aucune parcelle à surveiller pour le moment.
                </div>
              )}
            </div>
          </Card>

          <Card className="space-y-4">
            <div>
              <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Base conseiller / coopérative</div>
              <div className="mt-2 text-2xl font-semibold text-soil-900">Structure prête à étendre</div>
            </div>
            <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4 text-sm leading-6 text-soil-700">
              Modèle produit déjà aligné sur une organisation future avec un conseiller, plusieurs agriculteurs, plusieurs parcelles et plusieurs analyses par compte.
            </div>
            <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
              {latestEntries.map((entry) => (
                <div key={entry.analysis_id} className="rounded-2xl border border-soil-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Dernière activité</div>
                  <div className="mt-2 font-semibold text-soil-900">{entry.parcel?.name ?? entry.parcel_id ?? 'Parcelle inconnue'}</div>
                  <div className="mt-1 text-sm text-soil-500">{new Date(entry.created_at).toLocaleString('fr-FR')}</div>
                </div>
              ))}
              {!latestEntries.length ? <div className="rounded-2xl border border-dashed border-soil-200 bg-stone-50 p-4 text-sm text-soil-600">Les activités récentes apparaîtront ici.</div> : null}
            </div>
          </Card>
        </div>

        <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <Card>
            <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Lecture métier</div>
            <div className="mt-2 text-2xl font-semibold text-soil-900">Score, critique et suivi</div>
            <div className="mt-4 rounded-3xl border border-soil-200 bg-stone-50 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Score global</div>
                  <div className="mt-2 text-3xl font-semibold text-soil-900">{averageSoilScore}/100</div>
                </div>
                <div className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-soil-700 shadow-sm">{watchlist.length ? 'Surveillance active' : 'Aucune alerte'}</div>
              </div>
              <p className="mt-3 text-sm leading-6 text-soil-700">{criticalCount} parcelle(s) critique(s) ou à confirmer parmi les analyses récentes.</p>
            </div>
          </Card>

          <Card>
            <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Dernières activités</div>
            <div className="mt-2 text-2xl font-semibold text-soil-900">Suivi chronologique</div>
            <div className="mt-4 space-y-3">
              {latestEntries.length ? latestEntries.map((entry) => {
                const soil = getSoilScore(entry.prediction);
                return (
                  <div key={entry.analysis_id} className="rounded-2xl border border-soil-200 bg-white p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="font-semibold text-soil-900">{entry.parcel?.name ?? entry.parcel_id ?? 'Parcelle inconnue'}</div>
                        <div className="text-sm text-soil-500">{new Date(entry.created_at).toLocaleString('fr-FR')}</div>
                      </div>
                      <div className="rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold text-soil-700">{soil.status}</div>
                    </div>
                    <div className="mt-3 text-sm text-soil-600">Score sol {soil.score}/100 · focus {soil.focus}</div>
                  </div>
                );
              }) : <div className="rounded-2xl border border-dashed border-soil-200 bg-stone-50 p-4 text-sm text-soil-600">Connecte des analyses pour afficher une timeline utile.</div>}
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
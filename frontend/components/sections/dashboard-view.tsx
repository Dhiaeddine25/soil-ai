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
import { buildWatchlist, getFocusLabel, getNutrientLevelLabel, getSoilScore } from '@/lib/soil-insights';

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
  const watchlistLabel = watchlist[0] ? getFocusLabel(getSoilScore(watchlist[0].prediction).focus) : 'potassium';
  const overallStatus = averageSoilScore >= 80 ? 'Bon etat' : averageSoilScore >= 50 ? 'A surveiller' : 'Prioritaire';

  return (
    <section className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <Card className="space-y-4">
          <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Assistant agricole</div>
          <div className="text-3xl font-semibold text-soil-900">Etat global de vos parcelles</div>
          <div className="flex flex-wrap items-center gap-3 text-sm text-soil-600">
            <span className="rounded-full bg-soil-100 px-3 py-1 text-xs font-semibold text-soil-700">{overallStatus}</span>
            <span>Indice sante sol: {averageSoilScore}%</span>
            <span>{watchlist.length} parcelle(s) a surveiller</span>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/upload"><Button><Leaf className="h-4 w-4" />{messages.dashboard.openAnalysis}</Button></Link>
            <Link href="/history"><Button variant="ghost">{messages.dashboard.goToHistory}</Button></Link>
            <Link href="/parcels"><Button variant="ghost">{messages.dashboard.goToParcels}</Button></Link>
          </div>
          <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4 text-sm text-soil-700">
            {criticalCount} parcelle(s) critique(s) ou a confirmer. Priorite actuelle: {watchlistLabel}.
          </div>
        </Card>

        <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <Card className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Parcelles a surveiller</div>
                <div className="mt-2 text-2xl font-semibold text-soil-900">Alertes prioritaires</div>
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
                        {soil.score}%
                      </div>
                    </div>
                    <div className="mt-3 grid gap-2 sm:grid-cols-3">
                      <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">Potassium {getNutrientLevelLabel(entry.prediction?.prediction?.K_level)}</div>
                      <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">Azote {getNutrientLevelLabel(entry.prediction?.prediction?.N_level)}</div>
                      <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">Phosphore {getNutrientLevelLabel(entry.prediction?.prediction?.P_level)}</div>
                    </div>
                    <div className="mt-3 text-xs uppercase tracking-[0.18em] text-soil-500">{soil.status} · focus {getFocusLabel(soil.focus)}</div>
                  </Link>
                );
              }) : (
                <div className="rounded-2xl border border-dashed border-soil-200 bg-stone-50 p-4 text-sm text-soil-600">
                  Aucune parcelle a surveiller pour le moment.
                </div>
              )}
            </div>
          </Card>

          <Card className="space-y-4">
            <div>
              <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Dernieres analyses</div>
              <div className="mt-2 text-2xl font-semibold text-soil-900">Suivi recent</div>
            </div>
            <div className="space-y-3">
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
                    <div className="mt-3 text-sm text-soil-600">Indice sol {soil.score}% · focus {getFocusLabel(soil.focus)}</div>
                  </div>
                );
              }) : (
                <div className="rounded-2xl border border-dashed border-soil-200 bg-stone-50 p-4 text-sm text-soil-600">Connecte des analyses pour afficher une timeline utile.</div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
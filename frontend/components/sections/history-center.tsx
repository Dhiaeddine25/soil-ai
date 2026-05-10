"use client";

import Link from 'next/link';
import { Download, Loader2, Search } from 'lucide-react';
import { useEffect, useState, useTransition } from 'react';

import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';
import { downloadHistoryCsv, downloadHistoryPdf, getHistory, listParcels } from '@/lib/api';
import type { HistoryListResponse, ParcelPublic } from '@/lib/types';
import { parcelHistory, samplePrediction } from '@/lib/mock';
import { buildTimeline, getNutrientLevelLabel, getSoilScore } from '@/lib/soil-insights';

export function HistoryCenter() {
  const { user, token, loading } = useAuth();
  const { messages } = useI18n();
  const [history, setHistory] = useState<HistoryListResponse | null>(null);
  const [parcels, setParcels] = useState<ParcelPublic[]>([]);
  const [selectedParcelId, setSelectedParcelId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [isExporting, setIsExporting] = useState(false);

  const currentUserId = user?.id ?? 'guest';

  const loadHistory = (normalizedUserId: string, parcelId?: string) => {
    setError(null);
    startTransition(async () => {
      try {
        const response = await getHistory(normalizedUserId, token ?? undefined, parcelId);
        setHistory(response);
      } catch {
        setHistory({
          user_id: normalizedUserId,
          total: parcelHistory.length,
          entries: parcelHistory.map((item, index) => ({
            user_id: normalizedUserId,
            parcel_id: item.parcel,
            parcel: { id: `mock-parcel-${index}`, user_id: normalizedUserId, name: item.parcel, location: null, created_at: new Date().toISOString() },
            analysis_id: `mock-${index}`,
            created_at: new Date().toISOString(),
            prediction: {
              ...samplePrediction,
              prediction: { K_level: item.k as 'K0' | 'K1' | 'K2', N_level: item.n as 'N0' | 'N1' | 'N2', P_level: item.p as 'P0' | 'P1' },
              confidence: item.confidence,
              interpretation: 'Historique local en mode mock.',
              recommendation: item.status,
              timestamp: new Date().toISOString(),
              source: item.parcel,
            },
          })),
        });
        setError('Mode démo local activé.');
      }
    });
  };

  useEffect(() => {
    if (!loading && user && token) {
      void (async () => {
        try {
          const items = await listParcels(token);
          setParcels(items);
          setSelectedParcelId((current) => current || (items[0]?.id ?? ''));
        } catch {
          setParcels([]);
        }
      })();
    }
  }, [loading, user, token]);

  useEffect(() => {
    if (!loading && user && token) {
      loadHistory(currentUserId, selectedParcelId || undefined);
    }
  }, [loading, user, token, selectedParcelId]);

  const exportHistory = async (format: 'csv' | 'pdf') => {
    const normalizedUserId = currentUserId;
    setError(null);
    setIsExporting(true);
    try {
      const parcelId = selectedParcelId || undefined;
      if (format === 'csv') {
        await downloadHistoryCsv(normalizedUserId, token ?? undefined, parcelId);
      } else {
        await downloadHistoryPdf(normalizedUserId, token ?? undefined, parcelId);
      }
    } catch {
      setError('Export indisponible pour le moment.');
    } finally {
      setIsExporting(false);
    }
  };

  const entries = history?.entries ?? [];
  const timeline = buildTimeline(entries);

  return (
    <section className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <Card className="space-y-4">
          <div className="text-sm uppercase tracking-[0.18em] text-soil-500">{messages.history.title}</div>
          <div className="text-3xl font-semibold text-soil-900">{messages.history.subtitle}</div>
          <div className="grid gap-4 md:grid-cols-[1fr_auto] md:items-end">
            <label className="block space-y-2 text-sm font-medium text-soil-700">
              <span>{messages.history.filter}</span>
              <select value={selectedParcelId} onChange={(event) => setSelectedParcelId(event.target.value)} className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500">
                <option value="">Toutes les parcelles</option>
                {parcels.map((parcel) => <option key={parcel.id} value={parcel.id}>{parcel.name}{parcel.location ? ` - ${parcel.location}` : ''}</option>)}
              </select>
            </label>
            <Button type="button" onClick={() => loadHistory(currentUserId, selectedParcelId || undefined)} disabled={isPending}>
              {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              Charger
            </Button>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button type="button" variant="ghost" onClick={() => exportHistory('csv')} disabled={isExporting}><Download className="h-4 w-4" />{messages.history.exportCsv}</Button>
            <Button type="button" variant="ghost" onClick={() => exportHistory('pdf')} disabled={isExporting}><Download className="h-4 w-4" />{messages.history.exportPdf}</Button>
          </div>
          {error ? <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{error}</div> : null}
        </Card>

        <div className="grid gap-4 md:grid-cols-3">
          <Card><div className="text-sm text-soil-500">Analyses</div><div className="mt-2 text-3xl font-semibold text-soil-900">{history?.total ?? 0}</div></Card>
          <Card><div className="text-sm text-soil-500">Utilisateur</div><div className="mt-2 text-3xl font-semibold text-soil-900">{history?.user_id ?? currentUserId}</div></Card>
          <Card><div className="text-sm text-soil-500">Mode</div><div className="mt-2 text-3xl font-semibold text-soil-900">Connected</div></Card>
        </div>

        <Card>
          <div className="text-sm uppercase tracking-[0.18em] text-soil-500">{messages.history.title}</div>
          <div className="mt-4 space-y-3">
            {entries.length ? entries.map((entry) => {
              const prediction = entry.prediction;
              return (
                <Link key={entry.analysis_id} href={`/history/${entry.analysis_id}`} className="block rounded-2xl border border-soil-200 bg-white p-4 transition hover:border-leaf-300 hover:shadow-sm">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold text-soil-900">{entry.parcel?.name ?? entry.parcel_id ?? 'Parcelle inconnue'}</div>
                      <div className="text-sm text-soil-500">{new Date(entry.created_at).toLocaleString('fr-FR')}</div>
                    </div>
                    <div className={`rounded-full px-3 py-1 text-sm font-semibold ${prediction?.status === 'image_non_exploitable' ? 'bg-rose-100 text-rose-800' : prediction?.status === 'prediction_incertaine' ? 'bg-sky-100 text-sky-800' : prediction?.status === 'confirmation_recommandee' ? 'bg-amber-100 text-amber-800' : 'bg-leaf-100 text-leaf-800'}`}>
                      {prediction ? `${Math.round(prediction.confidence * 100)}%` : '—'}
                    </div>
                  </div>
                    <div className="mt-3 grid grid-cols-3 gap-2 text-sm text-soil-700">
                      <div className="rounded-xl bg-stone-50 px-3 py-2">Potassium {getNutrientLevelLabel(prediction?.prediction?.K_level)}</div>
                      <div className="rounded-xl bg-stone-50 px-3 py-2">Azote {getNutrientLevelLabel(prediction?.prediction?.N_level)}</div>
                      <div className="rounded-xl bg-stone-50 px-3 py-2">Phosphore {getNutrientLevelLabel(prediction?.prediction?.P_level)}</div>
                  </div>
                  <div className="mt-3 text-xs uppercase tracking-[0.18em] text-soil-500">{prediction?.status === 'ok' ? 'Analyse prête' : prediction?.status === 'prediction_incertaine' ? 'Résultat incertain' : prediction?.status === 'confirmation_recommandee' ? 'Confirmation recommandée' : 'Image non exploitable'}</div>
                </Link>
              );
            }) : <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4 text-sm text-soil-600">{messages.history.empty}</div>}
          </div>
        </Card>

        <Card className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Timeline de parcelle</div>
              <div className="mt-2 text-2xl font-semibold text-soil-900">Suivi chronologique des analyses</div>
            </div>
            <div className="rounded-full border border-soil-200 bg-white px-3 py-1 text-xs font-semibold text-soil-600">{timeline.length} entrée(s)</div>
          </div>

          <div className="space-y-3">
            {timeline.length ? timeline.map(({ entry, score, level, status }) => {
              const soil = getSoilScore(entry.prediction);
              return (
                <Link key={entry.analysis_id} href={`/history/${entry.analysis_id}`} className="block rounded-2xl border border-soil-200 bg-white p-4 transition hover:border-leaf-300 hover:shadow-sm">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold text-soil-900">{entry.parcel?.name ?? entry.parcel_id ?? 'Parcelle inconnue'}</div>
                      <div className="text-sm text-soil-500">{new Date(entry.created_at).toLocaleString('fr-FR')}</div>
                    </div>
                    <div className="rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold text-soil-700">{score}/100</div>
                  </div>
                  <div className="mt-3 grid gap-2 sm:grid-cols-4">
                    <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">Potassium {getNutrientLevelLabel(entry.prediction?.prediction?.K_level)}</div>
                    <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">Azote {getNutrientLevelLabel(entry.prediction?.prediction?.N_level)}</div>
                    <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">Phosphore {getNutrientLevelLabel(entry.prediction?.prediction?.P_level)}</div>
                    <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">{level}</div>
                  </div>
                  <div className="mt-3 text-xs uppercase tracking-[0.18em] text-soil-500">{soil.status} · {status}</div>
                </Link>
              );
            }) : <div className="rounded-2xl border border-dashed border-soil-200 bg-stone-50 p-4 text-sm text-soil-600">La timeline apparaîtra dès qu’une première analyse sera enregistrée.</div>}
          </div>
        </Card>
      </div>
    </section>
  );
}
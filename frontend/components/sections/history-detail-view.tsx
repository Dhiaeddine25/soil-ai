"use client";

import Link from 'next/link';
import { useEffect, useMemo, useState, useTransition } from 'react';
import { ArrowDownRight, ArrowLeft, ArrowUpRight, Clock3, Download, Loader2, Minus, MoveRight, RotateCcw } from 'lucide-react';

import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { AnalysisHero } from '@/components/ui/analysis-hero';
import { NutrientStatusCard } from '@/components/ui/nutrient-status-card';
import { ParcelTimeline } from '@/components/ui/parcel-timeline';
import { RefusalAnalysisCard } from '@/components/ui/refusal-analysis-card';
import { SmartAdviceCard } from '@/components/ui/smart-advice-card';
import { SoilHealthCard } from '@/components/ui/soil-health-card';
import DebugPanel from '@/components/ui/debug-panel';
import ComparisonCard from '@/components/ui/comparison-card';
import { QualityWarningCard } from '@/components/ui/quality-warning-card';
import { downloadHistoryCsv, downloadHistoryPdf, getHistory, getHistoryEntry } from '@/lib/api';
import { API_BASE } from '@/lib/api';
import type { HistoryEntry } from '@/lib/types';
import { comparePredictions, getFocusLabel, getNutrientLevelLabel, getSoilScore } from '@/lib/soil-insights';
import { useI18n } from '@/components/i18n/i18n-provider';

const imagePalettes = [
  'from-leaf-300 via-emerald-200 to-soil-100',
  'from-amber-300 via-orange-200 to-stone-100',
  'from-sky-300 via-cyan-200 to-teal-100',
  'from-rose-300 via-fuchsia-200 to-amber-100',
];

function pickPalette(key: string) {
  let seed = 0;
  for (let index = 0; index < key.length; index += 1) {
    seed = (seed * 31 + key.charCodeAt(index)) % imagePalettes.length;
  }
  return imagePalettes[seed];
}

export function HistoryDetailView({ analysisId }: { analysisId: string }) {
  const { user, token, loading } = useAuth();
  const [entry, setEntry] = useState<HistoryEntry | null>(null);
  const [relatedEntries, setRelatedEntries] = useState<HistoryEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [isExporting, setIsExporting] = useState(false);
  const [galleryLoading, setGalleryLoading] = useState(false);

  useEffect(() => {
    if (loading || !user || !token) {
      return;
    }

    startTransition(async () => {
      try {
        const detail = await getHistoryEntry(user.id, analysisId, token);
        setEntry(detail);
      } catch {
        setError('Analyse introuvable ou inaccessible.');
      }
    });
  }, [analysisId, loading, token, user]);

  useEffect(() => {
    if (loading || !user || !token || !entry?.parcel_id) {
      setRelatedEntries(entry ? [entry] : []);
      return;
    }

    let active = true;
    setGalleryLoading(true);

    void (async () => {
      try {
        const history = await getHistory(user.id, token, entry.parcel_id ?? undefined);
        if (active) {
          setRelatedEntries(history.entries);
        }
      } catch {
        if (active) {
          setRelatedEntries(entry ? [entry] : []);
        }
      } finally {
        if (active) {
          setGalleryLoading(false);
        }
      }
    })();

    return () => {
      active = false;
    };
  }, [entry, loading, token, user]);

  const prediction = entry?.prediction ?? null;
  const npkPrediction = prediction?.prediction ?? prediction?.npk_prediction ?? null;
  const exportParcelId = entry?.parcel_id ?? undefined;

  const { messages } = useI18n();
  const sourceLabel = useMemo(() => entry?.image_name ?? prediction?.source ?? (messages.history?.imageNotProvided ?? 'Image non renseignee'), [entry, prediction, messages]);

  const confidence = Math.round((prediction?.confidence ?? 0) * 100);
  const agronomicAdvice = prediction?.agronomic_advice;
  const status = prediction?.status ?? 'image_non_exploitable';
  const isRejected = status === 'image_non_exploitable';
  const globalSoil = getSoilScore(prediction);
  const orderedEntries = useMemo(
    () => [...relatedEntries].sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()),
    [relatedEntries],
  );
  const previousEntry = orderedEntries.find((item) => item.analysis_id !== entry?.analysis_id) ?? null;
  const comparison = useMemo(() => comparePredictions(previousEntry?.prediction ?? null, prediction), [previousEntry, prediction]);
  const previousScore = previousEntry?.prediction ? getSoilScore(previousEntry.prediction).score : null;
  const scoreDelta = previousScore === null ? null : globalSoil.score - previousScore;
  const previousConfidence = previousEntry?.prediction?.confidence ?? null;
  const confidenceDelta = previousConfidence === null ? null : Math.round(((prediction?.confidence ?? 0) - previousConfidence) * 100);

  const galleryItems = useMemo(() => (relatedEntries.length ? relatedEntries.slice(0, 6) : entry ? [entry] : []), [entry, relatedEntries]);

  const nutrientConfidence = (label?: string | null) => {
    if (!label) {
      return confidence;
    }
    const probability = prediction?.probabilities?.[label] ?? 0;
    return Math.round(probability * 100) || confidence;
  };

  const refusalTips = messages.history?.refusalTips ?? ['Reprendre une photo nette, sans ombre forte.', 'Cadrer le sol de pres, sans vegetation.', 'Eviter le flou en tenant le telephone stable.'];

  const timelineItems = useMemo(() => {
    const statusForScore = (score: number) => {
      if (score >= 75) {
        return { status: 'stable' as const, label: messages.history?.statusStable ?? 'Sol stable' };
      }
      if (score >= 55) {
        return { status: 'watch' as const, label: messages.history?.statusWatch ?? 'A surveiller' };
      }
      return { status: 'priority' as const, label: messages.history?.statusPriority ?? 'Prioritaire' };
    };

    return [...relatedEntries]
      .filter((item) => item.prediction)
      .sort((left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime())
      .map((item) => {
        const soil = getSoilScore(item.prediction);
        const focus = item.prediction?.agronomic_advice?.global_advice.priority_focus ?? 'P';
        const statusInfo = statusForScore(soil.score);
        return {
          id: item.analysis_id,
          dateLabel: new Date(item.created_at).toLocaleDateString('fr-FR'),
          score: soil.score,
          confidence: Math.round((item.prediction?.confidence ?? 0) * 100),
          status: statusInfo.status,
          statusLabel: statusInfo.label,
          nutrientLabel: getFocusLabel(focus),
          imageLabel: item.image_name ?? messages.history?.imageNotProvided ?? 'Image non renseignee',
        };
      });
  }, [relatedEntries, messages]);

  const trendConfig = {
    'amélioration': {
      label: 'Amelioration',
      icon: ArrowUpRight,
      tone: 'border-emerald-200 bg-emerald-50 text-emerald-800',
    },
    'baisse': {
      label: 'Baisse',
      icon: ArrowDownRight,
      tone: 'border-rose-200 bg-rose-50 text-rose-800',
    },
    'stable': {
      label: messages.history?.statusStable ?? 'Stable',
      icon: Minus,
      tone: 'border-soil-200 bg-soil-50 text-soil-700',
    },
  } as const;

  const adviceBody = prediction?.field_advice ?? prediction?.recommendation_message ?? prediction?.recommendation ?? messages.history?.adviceFallback ?? 'Conseil indicatif.';
  const adviceDisclaimer = prediction?.field_disclaimer ?? agronomicAdvice?.global_advice.warning ?? messages.history?.adviceDisclaimerFallback ?? 'Analyse indicative basee sur une image.';

  const exportContext = async (format: 'csv' | 'pdf') => {
    if (!user || !token) {
      return;
    }
    setIsExporting(true);
    try {
      if (format === 'csv') {
        await downloadHistoryCsv(user.id, token, exportParcelId);
      } else {
        await downloadHistoryPdf(user.id, token, exportParcelId);
      }
    } catch {
      setError(messages.history?.exportError ?? "Impossible d'exporter cet historique pour le moment.");
    } finally {
      setIsExporting(false);
    }
  };

  if (loading || isPending) {
    return (
      <div className="px-4 py-12 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl space-y-6">
          <div className="h-32 rounded-3xl border border-soil-100 bg-soil-50 p-6">
            <div className="h-4 w-24 rounded-full bg-soil-200" />
            <div className="mt-4 h-6 w-2/3 rounded-full bg-soil-200" />
            <div className="mt-6 h-3 w-1/3 rounded-full bg-soil-100" />
          </div>
          <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
            <div className="space-y-6">
              <div className="h-40 rounded-3xl border border-soil-100 bg-soil-50 animate-pulse" />
              <div className="grid gap-4 md:grid-cols-3">
                <div className="h-28 rounded-3xl border border-soil-100 bg-soil-50 animate-pulse" />
                <div className="h-28 rounded-3xl border border-soil-100 bg-soil-50 animate-pulse" />
                <div className="h-28 rounded-3xl border border-soil-100 bg-soil-50 animate-pulse" />
              </div>
              <div className="h-36 rounded-3xl border border-soil-100 bg-soil-50 animate-pulse" />
            </div>
            <div className="space-y-6">
              <div className="h-36 rounded-3xl border border-soil-100 bg-soil-50 animate-pulse" />
              <div className="h-56 rounded-3xl border border-soil-100 bg-soil-50 animate-pulse" />
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm text-soil-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            Chargement de l'analyse...
          </div>
        </div>
      </div>
    );
  }

  if (!entry) {
    return (
      <div className="px-4 py-12 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-xl rounded-3xl border border-soil-100 bg-soil-50 p-8 text-center">
          <div className="text-lg font-semibold text-soil-900">Analyse introuvable</div>
          <p className="mt-2 text-sm text-soil-600">L'analyse demandee n'est plus disponible ou n'appartient pas a ce compte.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <AnalysisHero
          parcelName={entry.parcel?.name ?? entry.parcel_id ?? 'Analyse sans parcelle'}
          dateLabel={new Date(entry.created_at).toLocaleString('fr-FR')}
          status={globalSoil.status}
          confidence={confidence}
          imageLabel={sourceLabel}
        />

        {entry.image_url ? (
          <Card className="overflow-hidden p-0">
            <img
              src={`${API_BASE}${entry.image_url}`}
              alt={entry.image_name ?? 'Image analysée'}
              className="h-80 w-full object-cover"
            />
          </Card>
        ) : null}

        {error ? (
          <Card className="border-amber-200 bg-amber-50 text-amber-900">
            {error}
          </Card>
        ) : null}

        {isRejected ? (
          <RefusalAnalysisCard message={prediction?.warning_message ?? 'Analyse impossible.'} tips={refusalTips} />
        ) : (
          <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
            <div className="space-y-6">
              {prediction ? <QualityWarningCard result={prediction} /> : null}

              <SoilHealthCard status={globalSoil.status} score={globalSoil.score} summary={globalSoil.summary} />
              <div className="grid gap-4 md:grid-cols-3">
                <NutrientStatusCard
                  label="Azote"
                  level={getNutrientLevelLabel(npkPrediction?.N_level)}
                  confidence={nutrientConfidence(npkPrediction?.N_level)}
                  note={agronomicAdvice?.nitrogen.advice ?? 'Surveiller le niveau d azote.'}
                />
                <NutrientStatusCard
                  label="Phosphore"
                  level={getNutrientLevelLabel(npkPrediction?.P_level)}
                  confidence={nutrientConfidence(npkPrediction?.P_level)}
                  note={agronomicAdvice?.phosphorus.advice ?? 'Surveiller le niveau de phosphore.'}
                />
                <NutrientStatusCard
                  label="Potassium"
                  level={getNutrientLevelLabel(npkPrediction?.K_level)}
                  confidence={nutrientConfidence(npkPrediction?.K_level)}
                  note={agronomicAdvice?.potassium.advice ?? 'Surveiller le niveau de potassium.'}
                />
              </div>
              <Card className="space-y-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Evolution du sol</div>
                    <div className="mt-2 text-2xl font-semibold text-soil-900">Comparaison avec l'analyse precedente</div>
                  </div>
                  <div className="rounded-full border border-soil-200 bg-soil-50 px-3 py-1 text-xs font-semibold text-soil-700">
                    {previousEntry ? '2 analyses comparees' : 'Aucun precedent'}
                  </div>
                </div>

                {previousEntry ? (
                  <div className="space-y-4">
                    <div className="grid gap-3 sm:grid-cols-3">
                      {[
                        { label: 'Azote', trend: comparison.N.trend },
                        { label: 'Phosphore', trend: comparison.P.trend },
                        { label: 'Potassium', trend: comparison.K.trend },
                      ].map((item) => {
                        const config = trendConfig[item.trend];
                        const TrendIcon = config.icon;
                        return (
                          <div key={item.label} className="rounded-2xl border border-soil-100 bg-white p-4">
                            <div className="text-xs uppercase tracking-[0.18em] text-soil-500">{item.label}</div>
                            <div className={`mt-3 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${config.tone}`}>
                              <TrendIcon className="h-3.5 w-3.5" />
                              {config.label}
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    <div className="grid gap-3 sm:grid-cols-2">
                      <div className="rounded-2xl border border-soil-100 bg-soil-50 p-4">
                        <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Score sante</div>
                        <div className="mt-2 text-2xl font-semibold text-soil-900">{globalSoil.score}/100</div>
                        <div className="mt-2 text-sm text-soil-600">
                          {scoreDelta === null ? 'Non disponible' : scoreDelta >= 0 ? `+${scoreDelta}` : `${scoreDelta}`} depuis la derniere analyse
                        </div>
                      </div>
                      <div className="rounded-2xl border border-soil-100 bg-soil-50 p-4">
                        <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Confiance globale</div>
                        <div className="mt-2 text-2xl font-semibold text-soil-900">{confidence}%</div>
                        <div className="mt-2 text-sm text-soil-600">
                          {confidenceDelta === null ? 'Non disponible' : confidenceDelta >= 0 ? `+${confidenceDelta}%` : `${confidenceDelta}%`} depuis la derniere analyse
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 grid gap-4 md:grid-cols-2">
                      <div>
                        <ComparisonCard comparison={comparison} />
                      </div>
                      <div>
                        {prediction?.debug ? <DebugPanel result={prediction} /> : null}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="rounded-2xl border border-dashed border-soil-200 bg-soil-50 p-4 text-sm text-soil-600">
                    Cette parcelle n'a pas encore d'historique. La prochaine analyse activera la comparaison.
                  </div>
                )}
              </Card>
              <SmartAdviceCard
                title="Conseil terrain intelligent"
                body={adviceBody}
                disclaimer={adviceDisclaimer}
              />
            </div>

            <div className="space-y-6">
              <Card className="space-y-4">
                <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Actions</div>
                <div className="flex flex-wrap gap-3">
                  <Link href="/history">
                    <Button>
                      <ArrowLeft className="h-4 w-4" />
                      Retour historique
                    </Button>
                  </Link>
                  <Button variant="ghost" onClick={() => void exportContext('csv')} disabled={isExporting}>
                    <Download className="h-4 w-4" />
                    Export CSV
                  </Button>
                  <Button variant="ghost" onClick={() => void exportContext('pdf')} disabled={isExporting}>
                    <Download className="h-4 w-4" />
                    Export PDF
                  </Button>
                  <Link href={entry.parcel_id ? `/parcels?focus=${encodeURIComponent(entry.parcel_id)}` : '/parcels'}>
                    <Button variant="ghost">Voir la parcelle</Button>
                  </Link>
                  <Link href={entry.parcel_id ? `/upload?parcel=${encodeURIComponent(entry.parcel_id)}` : '/upload'}>
                    <Button variant="ghost">
                      <RotateCcw className="h-4 w-4" />
                      Relancer une analyse
                    </Button>
                  </Link>
                </div>
              </Card>

              <ParcelTimeline items={timelineItems} />

              <Card className="space-y-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Mini galerie</div>
                    <div className="mt-2 text-2xl font-semibold text-soil-900">Historique visuel</div>
                  </div>
                  <div className="flex items-center gap-2 rounded-full border border-soil-200 bg-white px-3 py-2 text-xs font-semibold text-soil-600">
                    <Clock3 className="h-4 w-4" />
                    {galleryLoading ? 'Chargement...' : `${galleryItems.length} visuel(s)`}
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {galleryItems.length ? galleryItems.map((item) => {
                    const isCurrent = item.analysis_id === entry.analysis_id;
                    const itemPalette = pickPalette(item.image_name ?? item.analysis_id);
                    return (
                      <Link
                        key={item.analysis_id}
                        href={`/history/${item.analysis_id}`}
                        className={`group overflow-hidden rounded-[1.6rem] border transition hover:-translate-y-0.5 hover:shadow-lg ${isCurrent ? 'border-leaf-300 bg-leaf-50' : 'border-soil-100 bg-white'}`}
                      >
                        <div className={`relative aspect-[4/3] bg-gradient-to-br ${itemPalette} p-4`}>
                          <div className="relative flex h-full flex-col justify-between text-soil-950">
                            <div className="rounded-full bg-white/85 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-soil-600">
                              {isCurrent ? 'Analyse actuelle' : 'Analyse liee'}
                            </div>
                            <div className="rounded-2xl border border-white/40 bg-white/75 p-3 shadow-sm">
                              <div className="text-sm font-semibold text-soil-950">{item.image_name ?? 'Image non renseignee'}</div>
                              <div className="mt-1 text-xs text-soil-500">{new Date(item.created_at).toLocaleDateString('fr-FR')}</div>
                            </div>
                          </div>
                        </div>
                        <div className="space-y-2 p-4">
                          <div className="flex items-center justify-between gap-3">
                            <div className="text-sm font-semibold text-soil-900">{item.parcel?.name ?? item.parcel_id ?? 'Parcelle inconnue'}</div>
                            <MoveRight className="h-4 w-4 text-soil-400 transition group-hover:translate-x-0.5" />
                          </div>
                          <div className="text-xs uppercase tracking-[0.18em] text-soil-500">{new Date(item.created_at).toLocaleString('fr-FR')}</div>
                        </div>
                      </Link>
                    );
                  }) : (
                    <div className="col-span-full rounded-2xl border border-dashed border-soil-200 bg-soil-50 p-6 text-sm text-soil-600">
                      Aucune galerie disponible pour cette parcelle.
                    </div>
                  )}
                </div>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

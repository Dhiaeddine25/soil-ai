"use client";

import Link from 'next/link';
import { useEffect, useMemo, useState, useTransition } from 'react';
import { ArrowLeft, Clock3, Download, ImageOff, Loader2, MapPinned, MoveRight, RotateCcw, Sparkles } from 'lucide-react';

import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { downloadHistoryCsv, downloadHistoryPdf, getHistory, getHistoryEntry } from '@/lib/api';
import type { HistoryEntry } from '@/lib/types';
import { buildTimeline, comparePredictions, getNutrientLevelLabel, getSoilScore } from '@/lib/soil-insights';

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
  const exportParcelId = entry?.parcel_id ?? undefined;

  const sourceLabel = useMemo(() => {
    if (entry?.image_name) {
      return entry.image_name;
    }
    if (prediction?.source) {
      return prediction.source;
    }
    return 'Image non renseignée';
  }, [entry, prediction]);

  const confidence = Math.round((prediction?.confidence ?? 0) * 100);
  const palette = pickPalette(entry?.image_name ?? entry?.analysis_id ?? 'analysis');
  const agronomicAdvice = prediction?.agronomic_advice;
  const status = prediction?.status ?? 'image_non_exploitable';
  const isRejected = status === 'image_non_exploitable';
  const isUncertain = status === 'prediction_incertaine';
  const needsConfirmation = status === 'confirmation_recommandee';
  const timeline = useMemo(() => buildTimeline(relatedEntries), [relatedEntries]);
  const comparison = useMemo(() => {
    const ordered = [...relatedEntries].sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime());
    const previous = ordered.find((item) => item.analysis_id !== entry?.analysis_id) ?? null;
    return comparePredictions(previous?.prediction ?? null, prediction);
  }, [entry?.analysis_id, prediction, relatedEntries]);
  const globalSoil = getSoilScore(prediction);

  const galleryItems = useMemo(() => {
    if (relatedEntries.length) {
      return relatedEntries.slice(0, 6);
    }
    return entry ? [entry] : [];
  }, [entry, relatedEntries]);

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
      setError('Export indisponible pour cette analyse.');
    } finally {
      setIsExporting(false);
    }
  };

  if (loading || isPending) {
    return (
      <div className="px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl">
          <Card>
            <div className="flex items-center gap-3 text-soil-700">
              <Loader2 className="h-4 w-4 animate-spin" />
              Chargement du détail d’analyse...
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (error && !entry) {
    return (
      <div className="px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl space-y-4">
          <Card>
            <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Détail d'analyse</div>
            <h1 className="mt-2 text-3xl font-semibold text-soil-900">Analyse introuvable</h1>
            <p className="mt-3 text-sm text-soil-600">{error}</p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link href="/history">
                <Button>
                  <ArrowLeft className="h-4 w-4" />
                  Retour historique
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (!entry) {
    return null;
  }

  return (
    <div className="px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <Card className="overflow-hidden border-stone-200 bg-white p-0 shadow-[0_30px_80px_rgba(68,64,60,0.12)]">
          <div className="relative bg-white px-6 py-6 text-stone-900 sm:px-8 sm:py-8">
            <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-leaf-400 via-emerald-400 to-amber-300" />
            <div className="relative flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-sm uppercase tracking-[0.22em] text-stone-500">Détail d'analyse</div>
                <h1 className="mt-2 text-3xl font-semibold tracking-tight text-stone-900 sm:text-4xl">{entry.parcel?.name ?? entry.parcel_id ?? 'Analyse sans parcelle'}</h1>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-stone-700 sm:text-base">
                  Vue de démonstration premium: contexte parcelle, image d'entrée, score de confiance, interprétation métier et actions de pilotage.
                </p>
              </div>
              <div className={`rounded-full border px-4 py-2 text-sm font-semibold ${isRejected ? 'border-rose-200 bg-rose-50 text-rose-900' : needsConfirmation ? 'border-amber-200 bg-amber-50 text-amber-900' : isUncertain ? 'border-sky-200 bg-sky-50 text-sky-900' : 'border-stone-200 bg-stone-50 text-stone-900'}`}>
                {prediction ? `${confidence}% de confiance` : 'Analyse refusée'}
              </div>
            </div>

            <div className="relative mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
              <div className="overflow-hidden rounded-[2rem] border border-stone-200 bg-stone-50 p-4 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Image analysée</div>
                    <div className="mt-2 text-lg font-semibold text-stone-900">{sourceLabel}</div>
                  </div>
                  <div className="rounded-full bg-white px-3 py-1 text-xs font-medium text-stone-700 shadow-sm">{prediction?.model_status ?? 'rejected'}</div>
                </div>

                <div className={`mt-4 overflow-hidden rounded-[1.75rem] bg-gradient-to-br ${palette} p-5 text-stone-900`}>
                  <div className="flex min-h-[320px] flex-col justify-between rounded-[1.45rem] border border-stone-200 bg-white p-5 shadow-sm">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Aperçu visuel</div>
                        <div className="mt-2 max-w-xs text-2xl font-semibold leading-tight text-stone-900">
                          {entry.image_name ?? 'Capture de sol enregistrée dans l’historique'}
                        </div>
                      </div>
                      <div className="rounded-2xl bg-stone-100 p-3 text-stone-700 shadow-sm">
                        <ImageOff className="h-6 w-6" />
                      </div>
                    </div>

                    <div className="mt-10 grid gap-3 sm:grid-cols-3">
                      {[
                        { label: 'Date', value: new Date(entry.created_at).toLocaleString('fr-FR') },
                        { label: 'Parcelle', value: entry.parcel?.name ?? entry.parcel_id ?? 'Non renseignée' },
                        { label: 'ID analyse', value: entry.analysis_id.slice(0, 8).toUpperCase() },
                      ].map((item) => (
                        <div key={item.label} className="rounded-2xl border border-stone-200 bg-white p-3">
                          <div className="text-[11px] uppercase tracking-[0.18em] text-stone-500">{item.label}</div>
                          <div className="mt-2 text-sm font-semibold text-stone-900">{item.value}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-[2rem] border border-stone-200 bg-white p-4 shadow-sm sm:p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Lecture rapide</div>
                    <div className="mt-2 text-2xl font-semibold text-stone-900">Pré-diagnostic NPK</div>
                  </div>
                  <Sparkles className="h-5 w-5 text-leaf-600" />
                </div>

                {prediction?.prediction ? (
                  <div className="mt-5 grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                    {([
                      { nutrient: 'K', level: prediction.prediction.K_level, tone: 'from-emerald-400 to-leaf-500' },
                      { nutrient: 'N', level: prediction.prediction.N_level, tone: 'from-sky-400 to-cyan-500' },
                      { nutrient: 'P', level: prediction.prediction.P_level, tone: 'from-amber-400 to-orange-500' },
                    ] as const).map((item) => (
                      <div key={item.nutrient} className="rounded-[1.4rem] border border-stone-200 bg-stone-50 p-4 text-stone-900">
                        <div className="flex items-center justify-between gap-3">
                          <div className="text-xs uppercase tracking-[0.2em] text-stone-500">{item.nutrient}</div>
                          <div className={`h-2.5 w-16 rounded-full bg-gradient-to-r ${item.tone}`} />
                        </div>
                        <div className="mt-3 text-3xl font-semibold tracking-tight text-stone-900">{item.level}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mt-5 rounded-[1.4rem] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
                    Image non exploitable: aucune classe NPK n’a été retenue.
                  </div>
                )}

                <div className="mt-5 rounded-[1.4rem] border border-stone-200 bg-stone-50 p-4 text-stone-900">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Confiance</div>
                    <div className="text-sm font-semibold text-stone-900">{confidence}%</div>
                  </div>
                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-stone-200">
                    <div className="h-full rounded-full bg-gradient-to-r from-leaf-500 via-emerald-400 to-emerald-300" style={{ width: `${confidence}%` }} />
                  </div>
                </div>

                <div className="mt-5 rounded-[1.4rem] border border-stone-200 bg-white p-4 text-stone-900 shadow-sm">
                  <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Interprétation</div>
                  <p className="mt-2 text-sm leading-6 text-stone-700">{prediction?.interpretation ?? 'L’image ne permet pas une interprétation fiable.'}</p>
                </div>

                <div className="mt-4 rounded-[1.4rem] border border-stone-200 bg-stone-50 p-4 text-stone-900 shadow-sm">
                  <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Recommandation</div>
                  <p className="mt-2 text-sm leading-6 text-stone-700">{prediction?.recommendation_message ?? prediction?.recommendation ?? 'Reprendre une image plus exploitable.'}</p>
                </div>

                <div className="mt-4 rounded-[1.4rem] border border-stone-200 bg-white p-4 shadow-sm">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Score global du sol</div>
                      <div className="mt-1 text-lg font-semibold text-stone-900">{globalSoil.score}/100 · {globalSoil.level}</div>
                    </div>
                    <div className="rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">{globalSoil.status}</div>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-stone-700">{globalSoil.summary}</p>
                </div>

                {prediction ? (
                  <div className={`mt-4 rounded-[1.4rem] border p-4 text-stone-900 shadow-sm ${isRejected ? 'border-rose-200 bg-rose-50' : needsConfirmation ? 'border-amber-200 bg-amber-50' : isUncertain ? 'border-sky-200 bg-sky-50' : 'border-stone-200 bg-stone-50'}`}>
                    <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Statut</div>
                    <div className="mt-2 text-lg font-semibold text-stone-900">{prediction.status === 'ok' ? 'Analyse prête' : prediction.status === 'prediction_incertaine' ? 'Résultat incertain' : prediction.status === 'confirmation_recommandee' ? 'Confirmation recommandée' : 'Image non exploitable'}</div>
                    <p className="mt-2 text-sm leading-6 text-stone-700">{prediction.warning_message}</p>
                    <p className="mt-2 text-xs leading-5 text-stone-500">{prediction.can_trust_result ? 'Résultat exploitable avec prudence.' : 'Résultat non fiable: ne pas agir sans confirmation.'}</p>
                  </div>
                ) : null}

                {agronomicAdvice ? (
                  <div className="mt-4 space-y-4 rounded-[1.4rem] border border-stone-200 bg-white p-4 shadow-sm">
                    <div>
                      <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Conseil agronomique indicatif</div>
                      <div className="mt-2 text-lg font-semibold text-stone-900">État global et priorités par nutriment</div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                      {[
                        agronomicAdvice.potassium,
                        agronomicAdvice.nitrogen,
                        agronomicAdvice.phosphorus,
                      ].map((item) => (
                        <div key={item.nutrient} className="rounded-2xl border border-stone-200 bg-stone-50 p-4">
                          <div className="flex items-center justify-between gap-3">
                            <div className="text-xs uppercase tracking-[0.18em] text-stone-500">{item.nutrient === 'K' ? 'Potassium' : item.nutrient === 'N' ? 'Azote' : 'Phosphore'}</div>
                            <div className={`rounded-full px-3 py-1 text-xs font-semibold ${item.priority === 'high' ? 'bg-amber-100 text-amber-900' : item.priority === 'moderate' ? 'bg-sky-100 text-sky-900' : 'bg-emerald-100 text-emerald-900'}`}>
                              {item.priority === 'high' ? 'Élevée' : item.priority === 'moderate' ? 'Modérée' : 'Faible'}
                            </div>
                          </div>
                          <div className="mt-2 text-2xl font-semibold text-stone-900">{getNutrientLevelLabel(item.level)}</div>
                          <div className="mt-1 text-sm font-medium text-stone-700">{item.soil_status}</div>
                          <p className="mt-3 text-sm leading-6 text-stone-700">{item.advice}</p>
                        </div>
                      ))}
                    </div>

                    <div className="rounded-2xl border border-stone-200 bg-stone-50 p-4 text-stone-900">
                      <div className="text-xs uppercase tracking-[0.18em] text-stone-500">État global du sol</div>
                      <div className="mt-2 text-lg font-semibold text-stone-900">{agronomicAdvice.global_advice.soil_status}</div>
                      <p className="mt-2 text-sm leading-6 text-stone-700">{agronomicAdvice.global_advice.summary}</p>
                      <p className="mt-2 text-xs leading-5 text-stone-500">{agronomicAdvice.global_advice.warning}</p>
                    </div>
                  </div>
                ) : null}

                <div className="mt-4 rounded-[1.4rem] border border-stone-200 bg-white p-4 shadow-sm">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="text-xs uppercase tracking-[0.2em] text-stone-500">Comparaison</div>
                      <div className="mt-1 text-lg font-semibold text-stone-900">Par rapport à l’analyse précédente</div>
                    </div>
                    <div className="rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">{comparison.score}</div>
                  </div>
                  <div className="mt-4 grid gap-3 sm:grid-cols-4">
                    {[
                      { label: 'K', value: comparison.K.trend },
                      { label: 'N', value: comparison.N.trend },
                      { label: 'P', value: comparison.P.trend },
                      { label: 'Score', value: comparison.score },
                    ].map((item) => (
                      <div key={item.label} className="rounded-2xl border border-stone-200 bg-stone-50 p-3 text-sm text-stone-700">
                        <div className="text-xs uppercase tracking-[0.18em] text-stone-500">{item.label}</div>
                        <div className="mt-2 font-semibold text-stone-900">{item.value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <Card className="space-y-5">
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
                <Button variant="ghost">
                  <MapPinned className="h-4 w-4" />
                  Voir la parcelle
                </Button>
              </Link>
              <Link href={entry.parcel_id ? `/upload?parcel=${encodeURIComponent(entry.parcel_id)}` : '/upload'}>
                <Button variant="ghost">
                  <RotateCcw className="h-4 w-4" />
                  Relancer une analyse
                </Button>
              </Link>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {[
                ['Date', new Date(entry.created_at).toLocaleString('fr-FR')],
                ['Parcelle', entry.parcel?.name ?? entry.parcel_id ?? 'Non renseignée'],
                ['Image', sourceLabel],
              ].map(([label, value]) => (
                <div key={label} className="rounded-2xl border border-soil-100 bg-soil-50 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-soil-500">{label}</div>
                  <div className="mt-2 text-sm font-semibold leading-6 text-soil-900">{value as string}</div>
                </div>
              ))}
            </div>

            <div className="rounded-3xl border border-soil-100 bg-soil-50 p-5 text-sm leading-6 text-soil-700">
              <div className="font-semibold text-soil-900">Contexte produit</div>
              <div className="mt-2">• Analyse identifiée par <span className="font-semibold text-soil-900">{entry.analysis_id}</span>.</div>
              <div>• Parcelle stockée côté historique et résolue depuis le compte connecté.</div>
              <div>• Image persistée sous forme de nom de fichier quand elle est disponible.</div>
            </div>

            {error ? <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{error}</div> : null}
          </Card>

          <Card className="space-y-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Mini galerie</div>
                <div className="mt-2 text-2xl font-semibold text-soil-900">Historique visuel de la parcelle</div>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-soil-200 bg-white px-3 py-2 text-xs font-semibold text-soil-600">
                <Clock3 className="h-4 w-4" />
                {galleryLoading ? 'Chargement...' : `${galleryItems.length} visuel(s)`}
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
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
                      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.26),_transparent_35%),linear-gradient(180deg,rgba(255,255,255,0.05),rgba(43,36,29,0.08))]" />
                      <div className="relative flex h-full flex-col justify-between text-soil-950">
                        <div className="flex items-start justify-between gap-3">
                          <div className="rounded-full bg-white/85 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-soil-600">
                            {isCurrent ? 'Analyse actuelle' : 'Analyse liée'}
                          </div>
                          <div className="rounded-full bg-white/75 px-2 py-1 text-xs font-semibold text-soil-700">
                            {item.prediction ? `${Math.round(item.prediction.confidence * 100)}%` : '—'}
                          </div>
                        </div>
                        <div className="rounded-2xl border border-white/40 bg-white/75 p-3 shadow-sm backdrop-blur-sm">
                          <div className="text-sm font-semibold text-soil-950">{item.image_name ?? 'Image non renseignée'}</div>
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

          <Card className="space-y-4">
            <div>
              <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Timeline de parcelle</div>
              <div className="mt-2 text-2xl font-semibold text-soil-900">Évolution chronologique</div>
            </div>
            <div className="space-y-3">
              {timeline.length ? timeline.map(({ entry: timelineEntry, score, level, status: soilStatus }) => (
                <div key={timelineEntry.analysis_id} className="rounded-2xl border border-soil-200 bg-white p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold text-soil-900">{new Date(timelineEntry.created_at).toLocaleDateString('fr-FR')}</div>
                      <div className="text-sm text-soil-500">{timelineEntry.parcel?.name ?? timelineEntry.parcel_id ?? 'Parcelle inconnue'}</div>
                    </div>
                    <div className="rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold text-soil-700">{score}/100</div>
                  </div>
                  <div className="mt-3 grid gap-2 sm:grid-cols-3">
                    <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">K {timelineEntry.prediction?.prediction?.K_level ?? '—'}</div>
                    <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">N {timelineEntry.prediction?.prediction?.N_level ?? '—'}</div>
                    <div className="rounded-xl bg-stone-50 px-3 py-2 text-sm text-soil-700">P {timelineEntry.prediction?.prediction?.P_level ?? '—'}</div>
                  </div>
                  <div className="mt-3 text-xs uppercase tracking-[0.18em] text-soil-500">{level} · {soilStatus}</div>
                </div>
              )) : <div className="rounded-2xl border border-dashed border-soil-200 bg-stone-50 p-4 text-sm text-soil-600">Aucune timeline disponible pour cette parcelle.</div>}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

"use client";

import Link from 'next/link';
import { ChevronDown, ChevronUp, ImagePlus, Loader2, Sparkles } from 'lucide-react';
import { useEffect, useMemo, useState, useTransition } from 'react';

import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';
import { listParcels, predictImage } from '@/lib/api';
import type { ParcelPublic, PredictionResponse } from '@/lib/types';
import { samplePrediction } from '@/lib/mock';
import { getFocusLabel, getNutrientLevelLabel, getNutrientName, getPredictionStatusLabel, getPriorityLabel, getSoilScore, getSortedNutrientAdvice } from '@/lib/soil-insights';

const kClasses = ['K0', 'K1', 'K2'] as const;
const nClasses = ['N0', 'N1', 'N2'] as const;
const pClasses = ['P0', 'P1'] as const;
const photoChecklist = [
  'Photo nette et bien exposée',
  'Sol centré dans le cadre',
  'Éviter le flou et les ombres fortes',
  'Écarter les objets non pertinents',
] as const;

function getProbability(probabilities: Record<string, number>, label: string) {
  return probabilities[label] ?? 0;
}

function formatProbability(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function UploadLab({ initialParcelId }: { initialParcelId?: string }) {
  const { user, token, loading } = useAuth();
  const { messages } = useI18n();
  const [file, setFile] = useState<File | null>(null);
  const [parcels, setParcels] = useState<ParcelPublic[]>([]);
  const [parcelId, setParcelId] = useState('');
  const [result, setResult] = useState<PredictionResponse | null>(samplePrediction);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [showProbabilities, setShowProbabilities] = useState(false);

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  const status = result?.status ?? 'ok';
  const isRejected = status === 'image_non_exploitable';
  const isUncertain = status === 'prediction_incertaine';
  const needsConfirmation = status === 'confirmation_recommandee';

  useEffect(() => {
    const loadParcels = async () => {
      if (!token) {
        return;
      }

      try {
        const items = await listParcels(token);
        setParcels(items);
        setParcelId((current) => current || initialParcelId || (items[0]?.id ?? ''));
      } catch {
        setParcels([]);
      }
    };

    void loadParcels();
  }, [token, initialParcelId]);

  const connectedLabel = loading ? '...' : (user?.full_name ?? user?.email ?? 'Session active');
  const confidence = Math.round((result?.confidence ?? 0) * 100);
  const agronomicAdvice = result?.agronomic_advice;
  const soilInsight = getSoilScore(result);
  const priorityAdvice = getSortedNutrientAdvice(result);

  const resetAnalysis = () => {
    setFile(null);
    setResult(samplePrediction);
    setError(null);
    setShowProbabilities(false);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!file) {
      setError('Ajoute une image du sol pour lancer l’analyse.');
      return;
    }

    startTransition(async () => {
      try {
        const prediction = await predictImage(file, parcelId || undefined, token ?? undefined);
        setResult(prediction);
      } catch {
        setResult(samplePrediction);
        setError('Mode démo local activé.');
      }
    });
  };

  return (
    <section className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card className="space-y-5">
          <div>
            <div className="text-sm uppercase tracking-[0.18em] text-soil-500">{messages.analysis.title}</div>
            <div className="mt-2 text-3xl font-semibold text-soil-900">{messages.analysis.subtitle}</div>
            <div className="mt-2 text-sm text-soil-600">{connectedLabel}</div>
          </div>

          <div className="rounded-3xl border border-stone-200 bg-stone-50 p-4">
            <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Guide photo avant analyse</div>
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              {photoChecklist.map((item) => (
                <div key={item} className="flex items-start gap-2 rounded-2xl bg-white px-3 py-2 text-sm text-soil-700 shadow-sm">
                  <span className="mt-0.5 inline-flex h-5 w-5 items-center justify-center rounded-full bg-leaf-100 text-xs font-semibold text-leaf-700">✓</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <label className="block space-y-2 text-sm font-medium text-soil-700">
              <span>{messages.analysis.chooseParcel}</span>
              <select
                value={parcelId}
                onChange={(event) => setParcelId(event.target.value)}
                className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500"
                disabled={!parcels.length}
              >
                <option value="">{parcels.length ? messages.analysis.chooseParcel : messages.analysis.noParcel}</option>
                {parcels.map((parcel) => (
                  <option key={parcel.id} value={parcel.id}>
                    {parcel.name}{parcel.location ? ` - ${parcel.location}` : ''}
                  </option>
                ))}
              </select>
            </label>

            {!parcels.length ? (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
                {messages.analysis.noParcel} <Link href="/parcels" className="font-semibold underline">{messages.analysis.goToParcels}</Link>
              </div>
            ) : null}

            <label className="flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed border-soil-200 bg-stone-50 p-6 text-center transition hover:border-leaf-400 hover:bg-leaf-50">
              <ImagePlus className="h-10 w-10 text-leaf-600" />
              <span className="mt-4 text-lg font-semibold text-soil-900">{messages.analysis.upload}</span>
              <span className="mt-2 text-sm text-soil-500">JPG, PNG, JPEG</span>
              <input type="file" accept="image/*" className="hidden" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            </label>

            {file ? <div className="text-sm text-soil-600">{file.name}</div> : null}

            <div className="flex flex-wrap gap-3">
              <Button type="submit" disabled={isPending || !parcels.length}>
                {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                {messages.analysis.launch}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={resetAnalysis}
              >
                {messages.analysis.clear}
              </Button>
            </div>

            {error ? <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{error}</div> : null}
          </form>

          {previewUrl ? (
            <div className="overflow-hidden rounded-3xl border border-soil-100 bg-white">
              <img src={previewUrl} alt="Aperçu de l'image uploadée" className="h-56 w-full object-cover" />
            </div>
          ) : null}
        </Card>

        <div className="space-y-6">
          {isRejected && result ? (
            <Card className="border-rose-200 bg-rose-50 text-rose-950 shadow-[0_18px_50px_rgba(190,18,60,0.08)]">
              <div className="text-sm uppercase tracking-[0.2em] text-rose-600">Image non exploitable</div>
              <div className="mt-2 text-2xl font-semibold">L’image ne peut pas être interprétée</div>
              <p className="mt-3 text-sm leading-6 text-rose-900/80">{result.warning_message}</p>
              <div className="mt-4 rounded-2xl border border-rose-200 bg-white/80 p-4 text-sm text-rose-900">
                {result.recommendation_message}
              </div>
              <div className="mt-5 flex flex-wrap gap-3">
                <Button type="button" variant="secondary" onClick={resetAnalysis}>
                  Reprendre l'image
                </Button>
                <Button type="button" variant="ghost" onClick={() => setFile(null)}>
                  Choisir une autre image
                </Button>
              </div>
            </Card>
          ) : null}

          {!isRejected ? <Card className={`overflow-hidden border-stone-200 bg-white text-stone-900 shadow-[0_24px_70px_rgba(68,64,60,0.12)] ${needsConfirmation ? 'ring-1 ring-amber-200' : isUncertain ? 'ring-1 ring-sky-200' : ''}`}>
            <div className="flex items-start justify-between gap-4 border-b border-stone-200 pb-5">
              <div>
                <div className="text-sm uppercase tracking-[0.2em] text-stone-500">{messages.analysis.result}</div>
                <div className="mt-2 flex flex-wrap items-center gap-3">
                  <div className="text-2xl font-semibold tracking-tight text-stone-900">Résultat principal</div>
                  {needsConfirmation ? <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-900">Confirmation recommandée</span> : null}
                  {isUncertain ? <span className="rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-900">Prédiction incertaine</span> : null}
                  {status === 'ok' ? <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-900">{getPredictionStatusLabel(status)}</span> : null}
                </div>
                <p className="mt-2 max-w-xl text-sm leading-6 text-stone-700">
                  Les valeurs finales sont mises en avant pour une lecture immédiate sur mobile comme sur écran large.
                </p>
              </div>

              <div className="rounded-2xl border border-stone-200 bg-stone-50 px-4 py-3 text-right">
                <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Confiance globale</div>
                <div className="mt-1 text-3xl font-semibold text-stone-900">{confidence}%</div>
              </div>
            </div>

            {result?.prediction ? (
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                {([
                  { label: 'K final', value: result.prediction.K_level, tone: 'from-emerald-400 to-leaf-500' },
                  { label: 'N final', value: result.prediction.N_level, tone: 'from-sky-400 to-cyan-500' },
                  { label: 'P final', value: result.prediction.P_level, tone: 'from-amber-400 to-orange-500' },
                ] as const).map((item) => (
                  <div key={item.label} className="rounded-[1.35rem] border border-stone-200 bg-stone-50 p-4 shadow-sm">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-xs uppercase tracking-[0.18em] text-stone-500">{item.label}</div>
                      <div className={`h-2.5 w-14 rounded-full bg-gradient-to-r ${item.tone}`} />
                    </div>
                    <div className="mt-3 text-4xl font-semibold tracking-tight text-stone-900">{item.value}</div>
                  </div>
                ))}
              </div>
            ) : null}

            <div className="mt-6 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="rounded-[1.35rem] border border-stone-200 bg-white p-5 text-stone-900 shadow-sm">
                <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Interprétation simple</div>
                <p className="mt-3 text-sm leading-6 text-stone-700">{result?.interpretation}</p>
              </div>

              <div className="rounded-[1.35rem] border border-stone-200 bg-stone-50 p-5 text-stone-900 shadow-sm">
                <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Lecture rapide</div>
                <div className="mt-3 flex items-center justify-between gap-3">
                  <span className="text-sm text-stone-700">Score de confiance</span>
                  <span className="text-2xl font-semibold text-stone-900">{confidence}%</span>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-stone-200">
                  <div className="h-full rounded-full bg-gradient-to-r from-leaf-300 via-emerald-200 to-white" style={{ width: `${confidence}%` }} />
                </div>
                <p className="mt-3 text-sm leading-6 text-stone-700">{result?.recommendation_message ?? result?.recommendation}</p>
              </div>

              <div className="rounded-[1.35rem] border border-stone-200 bg-white p-5 text-stone-900 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Score global du sol</div>
                    <div className="mt-2 text-2xl font-semibold text-stone-900">{soilInsight.score}/100 · {soilInsight.status}</div>
                  </div>
                  <div className="rounded-full bg-stone-100 px-3 py-1 text-xs font-semibold text-stone-700">Focus {getFocusLabel(soilInsight.focus)}</div>
                </div>
                <p className="mt-3 text-sm leading-6 text-stone-700">{soilInsight.summary}</p>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap gap-3 border-t border-stone-200 pt-5">
              <Button
                type="button"
                variant="ghost"
                className="border-stone-200 bg-white text-stone-900 hover:bg-stone-50"
                onClick={() => setShowProbabilities((current) => !current)}
              >
                {showProbabilities ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                {showProbabilities ? 'Masquer les détails' : 'Afficher les probabilités'}
              </Button>
            </div>

            {showProbabilities ? (
              <div className="mt-5 rounded-[1.35rem] border border-stone-200 bg-white p-5 text-stone-900 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Probabilités détaillées</div>
                    <div className="mt-2 text-lg font-semibold text-stone-900">Classe finale choisie et scores par classe</div>
                  </div>
                  <div className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-xs font-medium text-stone-700">
                    Choix final: {result?.prediction?.K_level} / {result?.prediction?.N_level} / {result?.prediction?.P_level}
                  </div>
                </div>

                <div className="mt-5 grid gap-4 lg:grid-cols-3">
                  {[
                    { title: 'K', classes: kClasses, final: result?.prediction?.K_level },
                    { title: 'N', classes: nClasses, final: result?.prediction?.N_level },
                    { title: 'P', classes: pClasses, final: result?.prediction?.P_level },
                  ].map((group) => (
                    <div key={group.title} className="rounded-[1.2rem] border border-stone-200 bg-stone-50 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Classe {group.title}</div>
                        <div className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-stone-700 shadow-sm">Finale: {group.final}</div>
                      </div>
                      <div className="mt-4 space-y-3">
                        {group.classes.map((label) => {
                          const probability = getProbability(result?.probabilities ?? {}, label);
                          const isFinal = label === group.final;
                          return (
                            <div
                              key={label}
                              className={`rounded-2xl border p-3 ${isFinal ? 'border-stone-300 bg-white text-stone-900' : 'border-stone-200 bg-white text-stone-900'}`}
                            >
                              <div className="flex items-center justify-between gap-3">
                                <div className="font-semibold">{label}</div>
                                <div className="text-sm font-semibold">{formatProbability(probability)}</div>
                              </div>
                              <div className={`mt-2 h-2 overflow-hidden rounded-full ${isFinal ? 'bg-stone-200' : 'bg-stone-100'}`}>
                                <div
                                  className={`h-full rounded-full ${isFinal ? 'bg-stone-900' : 'bg-gradient-to-r from-leaf-400 via-emerald-300 to-emerald-100'}`}
                                  style={{ width: `${Math.max(probability * 100, 4)}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
            </Card> : null}

          <Card>
            <div className="text-sm uppercase tracking-[0.2em] text-soil-500">{messages.analysis.recommendation}</div>
            <div className="mt-3 text-lg font-semibold text-soil-900">{result?.recommendation_message ?? result?.recommendation}</div>
            {result?.warning_message ? <div className="mt-3 text-sm leading-6 text-soil-600">{result.warning_message}</div> : null}
          </Card>

          {agronomicAdvice ? (
            <Card className="space-y-5">
              <div>
                <div className="text-sm uppercase tracking-[0.2em] text-soil-500">Conseil agronomique indicatif</div>
                <div className="mt-2 text-2xl font-semibold text-soil-900">Lecture prudente par nutriment</div>
                <p className="mt-2 text-sm leading-6 text-soil-600">
                  Ce bloc résume la priorité de suivi par nutriment et l’état global du sol, sans fournir de dose d’engrais.
                </p>
                <p className="mt-2 text-sm leading-6 text-soil-700">{agronomicAdvice.global_advice.priority_summary}</p>
              </div>

              <div className="grid gap-3 md:grid-cols-3">
                {priorityAdvice.map((item) => (
                  <div key={item.nutrient} className="rounded-[1.35rem] border border-stone-200 bg-stone-50 p-4 shadow-sm">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-xs uppercase tracking-[0.18em] text-stone-500">{getNutrientName(item.nutrient as 'K' | 'N' | 'P')}</div>
                      <div className={`rounded-full px-3 py-1 text-xs font-semibold ${item.priority === 'high' ? 'bg-amber-100 text-amber-900' : item.priority === 'moderate' ? 'bg-sky-100 text-sky-900' : 'bg-emerald-100 text-emerald-900'}`}>
                        Priorité {getPriorityLabel(item.priority)}
                      </div>
                    </div>
                    <div className="mt-3 text-3xl font-semibold tracking-tight text-stone-900">{getNutrientLevelLabel(item.level)}</div>
                    <div className="mt-2 text-sm font-medium text-stone-700">{item.soil_status}</div>
                    <p className="mt-3 text-sm leading-6 text-stone-700">{item.advice}</p>
                    <p className="mt-2 text-xs leading-5 text-stone-500">{item.summary}</p>
                  </div>
                ))}
              </div>

              <div className="rounded-[1.35rem] border border-stone-200 bg-white p-5 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="text-xs uppercase tracking-[0.18em] text-stone-500">État global du sol</div>
                    <div className="mt-2 text-xl font-semibold text-stone-900">{agronomicAdvice.global_advice.soil_status}</div>
                  </div>
                  <div className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-xs font-medium text-stone-600">
                    Score {agronomicAdvice.global_advice.soil_score}/100 · {agronomicAdvice.global_advice.soil_level}
                  </div>
                </div>
                <p className="mt-3 text-sm leading-6 text-stone-700">{agronomicAdvice.global_advice.summary}</p>
                <p className="mt-3 text-xs leading-5 text-stone-500">{agronomicAdvice.global_advice.warning}</p>
              </div>
            </Card>
          ) : null}
        </div>
      </div>
    </section>
  );
}

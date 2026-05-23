"use client";

import Link from 'next/link';
import { ImagePlus, Loader2, Sparkles } from 'lucide-react';
import { useEffect, useMemo, useState, useTransition } from 'react';

import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { AdviceCard } from '@/components/ui/advice-card';
import { AgricultureCard } from '@/components/ui/agriculture-card';
import { ConfidenceIndicator } from '@/components/ui/confidence-indicator';
import { NutrientCard } from '@/components/ui/nutrient-card';
import DebugPanel from '@/components/ui/debug-panel';
import { RefusalCard } from '@/components/ui/refusal-card';
import { SoilStatusCard } from '@/components/ui/soil-status-card';
import { useI18n } from '@/components/i18n/i18n-provider';
import { listParcels, predictImage } from '@/lib/api';
import type { ParcelPublic, PredictionResponse } from '@/lib/types';
import { getFocusLabel, getNutrientLevelLabel, getPredictionStatusLabel, getSoilScore } from '@/lib/soil-insights';
const photoChecklist = [
  'Photo nette et bien exposée',
  'Sol centré dans le cadre',
  'Éviter le flou et les ombres fortes',
  'Écarter les objets non pertinents',
] as const;

function getProbability(probabilities: Record<string, number>, label: string) {
  return probabilities[label] ?? 0;
}


export function UploadLab({ initialParcelId }: { initialParcelId?: string }) {
  const { user, token, loading } = useAuth();
  const { messages } = useI18n();
  const [file, setFile] = useState<File | null>(null);
  const [parcels, setParcels] = useState<ParcelPublic[]>([]);
  const [parcelId, setParcelId] = useState('');
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  const status = result?.status ?? 'ok';
  const isRejected = status === 'image_non_exploitable';

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

  const resetAnalysis = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  const refusalTips = [
    'Reprendre la photo',
    'Améliorer la lumière',
    'Rapprocher le sol',
    'Éviter les ombres',
    'Éviter les objets parasites',
  ];

  const nutrientConfidence = (label?: string | null) => {
    if (!label) {
      return confidence;
    }
    const probability = getProbability(result?.probabilities ?? {}, label);
    return Math.round(probability * 100) || confidence;
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
      } catch (analysisError) {
        setResult(null);
        setError(analysisError instanceof Error ? analysisError.message : 'Analyse impossible pour le moment.');
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
              <Button type="submit" disabled={isPending}>
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
            <RefusalCard
              title="Photo refusée : image non exploitable"
              message={result.refusal_reason ?? result.warning_message}
              tips={refusalTips}
              action={(
                <>
                  <Button type="button" variant="secondary" onClick={resetAnalysis}>
                    Reprendre l'image
                  </Button>
                  <Button type="button" variant="ghost" onClick={() => setFile(null)}>
                    Choisir une autre image
                  </Button>
                </>
              )}
            />
          ) : null}

          {!isRejected && result ? (
            <div className="space-y-6">
              <AgricultureCard className="space-y-4">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="text-sm uppercase tracking-[0.2em] text-soil-500">{messages.analysis.result}</div>
                  <span className="rounded-full bg-soil-100 px-3 py-1 text-xs font-semibold text-soil-700">
                    {getPredictionStatusLabel(status)}
                  </span>
                </div>
                <div className="text-2xl font-semibold text-soil-900">Lecture principale</div>
                <p className="text-sm leading-6 text-soil-600">{result.interpretation}</p>
                <ConfidenceIndicator value={confidence} />
              </AgricultureCard>

              <SoilStatusCard
                status={soilInsight.status}
                score={soilInsight.score}
                level={soilInsight.level}
                summary={soilInsight.summary}
                focus={getFocusLabel(soilInsight.focus)}
              />

              <div className="grid gap-4 md:grid-cols-3">
                {(
                  [
                    { key: 'N', label: 'Azote', advice: agronomicAdvice?.nitrogen, fallback: 'Surveiller le niveau d’azote.' },
                    { key: 'P', label: 'Phosphore', advice: agronomicAdvice?.phosphorus, fallback: 'Verifier l’apport en phosphore.' },
                    { key: 'K', label: 'Potassium', advice: agronomicAdvice?.potassium, fallback: 'Observer le potassium.' },
                  ] as const
                ).map((item) => (
                  <NutrientCard
                    key={item.label}
                    name={item.label}
                    level={getNutrientLevelLabel(result?.prediction?.[`${item.key}_level` as 'K_level' | 'N_level' | 'P_level'])}
                    confidence={nutrientConfidence(result?.prediction?.[`${item.key}_level` as 'K_level' | 'N_level' | 'P_level'])}
                    advice={item.advice?.advice ?? item.fallback}
                    status={item.advice?.soil_status}
                  />
                ))}
              </div>

              <AdviceCard
                title="Conseil terrain"
                body={result.recommendation_message ?? result.recommendation}
                disclaimer={agronomicAdvice?.global_advice.warning ?? 'Conseil indicatif base sur une analyse d’image.'}
              />

              {result?.debug ? (
                <div className="mt-4">
                  <DebugPanel result={result} />
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}

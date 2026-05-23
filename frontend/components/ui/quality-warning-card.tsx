import { AlertTriangle } from 'lucide-react';

import type { PredictionResponse } from '@/lib/types';

import { Card } from './card';

type QualityWarningCardProps = {
  result: PredictionResponse;
  className?: string;
};

export function QualityWarningCard({ result, className }: QualityWarningCardProps) {
  const imageQuality = result.image_quality;
  const qualityScore = imageQuality?.image_quality_score ?? result.image_quality_score;
  const warning = imageQuality?.warning ?? result.warning;
  const hasWarning = warning === 'low_image_quality' || (qualityScore !== undefined && qualityScore !== null && qualityScore < 65) || (result.quality_check?.issues?.length ?? 0) > 0;

  if (!hasWarning) {
    return null;
  }

  const recommendations = imageQuality?.recommendations?.length
    ? imageQuality.recommendations
    : result.recommendations?.length
      ? result.recommendations
    : [
        'Reprendre la photo avec plus de lumière.',
        'Stabiliser le téléphone pour réduire le flou.',
        'Cadrer davantage le sol.',
      ];

  const message = result.warning_message || 'Qualité d’image faible: la prédiction reste disponible, mais les résultats doivent être interprétés avec prudence.';

  return (
    <Card className={className ? `${className} border-amber-200 bg-amber-50 text-amber-950` : 'border-amber-200 bg-amber-50 text-amber-950'}>
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-amber-100 text-amber-700">
          <AlertTriangle className="h-5 w-5" />
        </span>
        <div className="min-w-0 flex-1 space-y-3">
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-amber-700">Avertissement qualité</div>
            <div className="mt-1 text-lg font-semibold text-amber-950">Image à surveiller, prédiction conservée</div>
          </div>
          <p className="text-sm leading-6 text-amber-900/90">{message}</p>
          {typeof qualityScore === 'number' ? (
            <div className="inline-flex rounded-full border border-amber-200 bg-white px-3 py-1 text-xs font-semibold text-amber-800">
              Score qualité image: {Math.round(qualityScore)}/100
            </div>
          ) : null}
          <div className="rounded-2xl border border-amber-200 bg-white/80 p-4 text-sm text-amber-900">
            <div className="text-xs uppercase tracking-[0.2em] text-amber-700">Recommandations</div>
            <ul className="mt-2 list-disc space-y-1 pl-4">
              {recommendations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </Card>
  );
}

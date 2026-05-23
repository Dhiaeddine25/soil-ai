'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';
import type { PredictionResponse } from '@/lib/types';
import { getSoilScore } from '@/lib/soil-insights';
import { AdviceCard } from '@/components/ui/advice-card';
import { AgricultureCard } from '@/components/ui/agriculture-card';
import { ConfidenceIndicator } from '@/components/ui/confidence-indicator';
import { NutrientCard } from '@/components/ui/nutrient-card';
import { QualityWarningCard } from '@/components/ui/quality-warning-card';
import { SoilStatusCard } from '@/components/ui/soil-status-card';

interface MobileAnalysisResultProps {
  result: PredictionResponse;
  onReset: () => void;
  onExportPDF: () => void;
  onExportCSV: () => void;
}

export function MobileAnalysisResult({ 
  result, 
  onReset, 
  onExportPDF, 
  onExportCSV 
}: MobileAnalysisResultProps) {
  const { messages } = useI18n();
  const confidence = Math.round((result.confidence ?? 0) * 100);
  const agronomicAdvice = result.agronomic_advice;
  const soilInsight = getSoilScore(result);
  const status = result.status ?? 'ok';
  const prediction = result.prediction ?? result.npk_prediction ?? null;

  const getProbability = (probabilities: Record<string, number>, label: string) => {
    return probabilities[label] ?? 0;
  };

  const nutrientConfidence = (label?: string | null) => {
    if (!label) {
      return confidence;
    }
    const probability = getProbability(result.probabilities ?? {}, label);
    return Math.round(probability * 100) || confidence;
  };

  return (
    <Card className="space-y-6">
      {/* Header with actions */}
      <div className="flex justify-between items-center pb-3 border-b border-soil-100">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-full bg-leaf-100 flex items-center justify-center">
            <svg className="h-5 w-5 text-leaf-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m2 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-soil-900">
            Analyse du sol
          </h3>
        </div>
        <div className="flex space-x-2">
          <Button
            onClick={onExportPDF}
            variant="ghost"
          >
            <svg className="h-4 w-4 text-soil-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 14h6m-6-4h6m2-7h6a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2 2v-6a2 2 0 012-2z" />
            </svg>
          </Button>
          <Button
            onClick={onExportCSV}
            variant="ghost"
          >
            <svg className="h-4 w-4 text-soil-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5h6M5 9h6a2 2 0 002 2v2a2 2 0 01-2 2H5a2 2 0 002-2zm0 0l3 3m-3-3l3 3" />
            </svg>
          </Button>
          <Button
            onClick={onReset}
            variant="secondary"
          >
            Nouvelle analyse
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="space-y-5">
        <QualityWarningCard result={result} />

        {/* Status and confidence */}
        <div className="flex items-center justify-between px-3 py-2 bg-leaf-50 rounded-xl">
          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              status === 'ok' 
                ? 'bg-leaf-100 text-leaf-800' 
                : status === 'prediction_incertaine' 
                  ? 'bg-amber-100 text-amber-800' 
                  : 'bg-soil-100 text-soil-800'
            }`}>
              {status === 'ok' 
                ? 'Résultat fiable' 
                : status === 'prediction_incertaine' 
                  ? 'Résultat incertain' 
                  : 'Confirmation recommandée'}
            </span>
          </div>
          <div className="h-8 w-8">
            <ConfidenceIndicator value={confidence} />
          </div>
        </div>

        {/* Main prediction */}
        <AgricultureCard className="space-y-4">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <div className="text-sm uppercase tracking-[0.2em] text-soil-500">
              Résultat
            </div>
            <span className={`rounded-full bg-soil-100 px-3 py-1 text-xs font-semibold text-soil-700`}>
                {prediction?.K_level ?? 'K0'} / {prediction?.N_level ?? 'N0'} / {prediction?.P_level ?? 'P0'}
            </span>
          </div>
          <div className="text-2xl font-semibold text-soil-900">
            Lecture principale
          </div>
          <p className="text-sm leading-6 text-soil-600">
            {result.interpretation}
          </p>
        </AgricultureCard>

        {/* Soil status */}
        <div className="mb-4">
          <SoilStatusCard
            status={soilInsight.status}
            score={soilInsight.score}
            level={soilInsight.level}
            summary={soilInsight.summary}
            focus={/* TODO: implement getFocusLabel */ ''}
          />
        </div>

        {/* Nutrients */}
        <div className="grid gap-4 md:grid-cols-3">
          {[
            { key: 'N', label: 'Azote', advice: agronomicAdvice?.nitrogen, fallback: 'Surveiller le niveau d’azote.' },
            { key: 'P', label: 'Phosphore', advice: agronomicAdvice?.phosphorus, fallback: 'Verifier l’apport en phosphore.' },
            { key: 'K', label: 'Potassium', advice: agronomicAdvice?.potassium, fallback: 'Observer le potassium.' },
          ].map((item) => (
            <NutrientCard
              key={item.label}
              name={item.label}
              level={/* TODO: implement getNutrientLevelLabel */ ''}
              confidence={nutrientConfidence(prediction?.[`${item.key}_level` as 'K_level' | 'N_level' | 'P_level'])}
              advice={item.advice?.advice ?? item.fallback}
              status={item.advice?.soil_status}
            />
          ))}
        </div>

        {/* Field advice */}
        <AdviceCard
          title="Conseil terrain"
          body={result.recommendation_message ?? result.recommendation}
          disclaimer={agronomicAdvice?.global_advice.warning ?? 'Conseil indicatif basé sur une analyse d’image.'}
        />
      </div>
    </Card>
  );
}
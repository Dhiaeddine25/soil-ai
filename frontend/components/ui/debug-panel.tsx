"use client";

import React from 'react';
import type { PredictionResponse, NutrientPredictionDetail } from '@/lib/types';

function renderProbList(list?: number[] | null) {
  if (!list) return <em>—</em>;
  return (
    <div className="text-xs text-soil-700">
      {list.map((v, i) => (
        <div key={i} className="flex justify-between">
          <span>#{i + 1}</span>
          <span>{Math.round((v ?? 0) * 100000) / 1000}%</span>
        </div>
      ))}
    </div>
  );
}

export function DebugPanel({ result }: { result: PredictionResponse }) {
  const nit = result.nitrogen as NutrientPredictionDetail | undefined | null;
  const phos = result.phosphorus as NutrientPredictionDetail | undefined | null;
  const pot = result.potassium as NutrientPredictionDetail | undefined | null;

  if (!result) return null;

  return (
    <div className="rounded-2xl border border-soil-100 bg-white p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Données probabilistes (debug)</div>
      <div className="mt-3 grid gap-4 md:grid-cols-3">
        {[{ key: 'N', detail: nit }, { key: 'P', detail: phos }, { key: 'K', detail: pot }].map((item) => (
          <div key={item.key} className="rounded-2xl border border-soil-100 bg-soil-50 p-3">
            <div className="text-sm font-semibold text-soil-900">{item.key}</div>
            <div className="mt-2 text-xs text-soil-600">Confidence: {Math.round((item.detail?.confidence ?? 0) * 100)}%</div>
            <div className="mt-2 text-[11px] text-soil-500">Raw probabilities</div>
            {renderProbList(item.detail?.raw_probabilities ?? null)}
            <div className="mt-2 text-[11px] text-soil-500">Calibrated probabilities</div>
            {renderProbList(item.detail?.calibrated_probabilities ?? null)}
            <div className="mt-2 text-xs text-soil-600">Entropy: {typeof item.detail?.raw_entropy === 'number' ? item.detail?.raw_entropy : '—'} → {typeof item.detail?.calibrated_entropy === 'number' ? item.detail?.calibrated_entropy : '—'}</div>
            <div className="mt-1 text-xs text-soil-600">Entropy baseline: {item.detail?.entropy_baseline ?? '—'}</div>
            <div className="mt-1 text-xs text-soil-600">Calibration factor: {item.detail?.calibration_factor ?? '—'}</div>
            <div className="mt-1 text-xs text-soil-600">Uncertainty adj: {item.detail?.uncertainty_adjustment ?? '—'}</div>
          </div>
        ))}
      </div>
      <div className="mt-3 text-xs text-soil-500">Soil health score: {result.soil_health_score ?? result.score ?? '—'}</div>
    </div>
  );
}

export default DebugPanel;

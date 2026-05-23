"use client";

import React from 'react';

export default function ComparisonCard({ comparison }: { comparison: any }) {
  if (!comparison) return null;

  const { similarity, rawSimilarity, entropyDiff, confidenceSpreadDiff, possibleCollapse } = comparison;

  return (
    <div className="rounded-2xl border border-soil-100 bg-white p-3">
      <div className="text-xs font-semibold text-soil-700">Comparison</div>
      <div className="mt-2 flex items-center justify-between">
        <div className="text-sm">Similarity</div>
        <div className="text-lg font-bold">{(similarity ?? 0).toFixed(3)}</div>
      </div>
      <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-soil-600">
        <div>Raw sim: {(rawSimilarity ?? 0).toFixed(3)}</div>
        <div>Entropy Δ: {typeof entropyDiff === 'number' ? entropyDiff.toFixed(4) : '—'}</div>
        <div>Conf spread Δ: {typeof confidenceSpreadDiff === 'number' ? confidenceSpreadDiff.toFixed(4) : '—'}</div>
        <div className="text-right">{possibleCollapse ? <span className="text-amber-700 font-semibold">POSSIBLE OUTPUT COLLAPSE</span> : <span className="text-soil-500">OK</span>}</div>
      </div>
    </div>
  );
}

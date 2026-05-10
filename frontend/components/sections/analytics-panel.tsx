"use client";

import { BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip, LineChart, Line, CartesianGrid, Legend } from 'recharts';

import { Card } from '@/components/ui/card';
import type { ResultsSummaryResponse } from '@/lib/types';
import { parcelHistory } from '@/lib/mock';

const compareData = [
  { model: 'EfficientNetV2L', valid: 91.15, test: 86.36 },
  { model: 'DenseNet201', valid: 89.82, test: 85.91 },
  { model: 'MobileNetV2', valid: 85.84, test: 79.09 },
];

const nutrientTrend = [
  { label: 'K0', score: 89.4 },
  { label: 'K1', score: 86.7 },
  { label: 'K2', score: 90.3 },
  { label: 'N0', score: 92.9 },
  { label: 'N1', score: 96.5 },
  { label: 'N2', score: 92.9 },
  { label: 'P0', score: 90.3 },
  { label: 'P1', score: 90.3 },
];

export function AnalyticsPanel({ results }: { results: ResultsSummaryResponse }) {
  const models = results.models;
  const bestModel = results.best_model;
  const uniqueParcels = new Set(parcelHistory.map((item) => item.parcel)).size;
  const averageConfidence = Math.round((parcelHistory.reduce((sum, item) => sum + item.confidence, 0) / Math.max(parcelHistory.length, 1)) * 100);
  const priorityCounts = parcelHistory.reduce<Record<string, number>>((counts, item) => {
    counts[item.priorityFocus] = (counts[item.priorityFocus] ?? 0) + 1;
    return counts;
  }, {});
  const dominantPriority = Object.entries(priorityCounts).sort((left, right) => right[1] - left[1])[0]?.[0] ?? 'P';
  const statusCounts = parcelHistory.reduce<Record<string, number>>((counts, item) => {
    counts[item.status] = (counts[item.status] ?? 0) + 1;
    return counts;
  }, {});

  return (
    <section className="px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <div className="text-sm text-soil-500">Best model</div>
            <div className="mt-2 text-2xl font-semibold text-soil-900">{bestModel.model_name}</div>
          </Card>
          <Card>
            <div className="text-sm text-soil-500">Hamming accuracy</div>
            <div className="mt-2 text-3xl font-semibold text-soil-900">{((bestModel.hamming_accuracy ?? 0) * 100).toFixed(2)}%</div>
          </Card>
          <Card>
            <div className="text-sm text-soil-500">Modèles comparés</div>
            <div className="mt-2 text-3xl font-semibold text-soil-900">{models.length}</div>
          </Card>
          <Card>
            <div className="text-sm text-soil-500">Parcelles suivies</div>
            <div className="mt-2 text-3xl font-semibold text-soil-900">{uniqueParcels}</div>
          </Card>
        </div>

        <Card className="space-y-4">
          <div>
            <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Analytics métier</div>
            <div className="mt-2 text-2xl font-semibold text-soil-900">Lecture opérationnelle du projet</div>
          </div>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Analyses démo</div>
              <div className="mt-2 text-3xl font-semibold text-soil-900">{parcelHistory.length}</div>
            </div>
            <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Score moyen</div>
              <div className="mt-2 text-3xl font-semibold text-soil-900">{averageConfidence}%</div>
            </div>
            <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Nutriment prioritaire</div>
              <div className="mt-2 text-3xl font-semibold text-soil-900">{dominantPriority}</div>
            </div>
            <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Statuts</div>
              <div className="mt-2 text-3xl font-semibold text-soil-900">{Object.keys(statusCounts).length}</div>
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
            <div className="rounded-2xl border border-soil-200 bg-white p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Répartition des statuts</div>
              <div className="mt-4 space-y-3">
                {Object.entries(statusCounts).map(([status, count]) => (
                  <div key={status}>
                    <div className="flex items-center justify-between gap-3 text-sm text-soil-700">
                      <span>{status}</span>
                      <span>{count}</span>
                    </div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-stone-200">
                      <div className="h-full rounded-full bg-gradient-to-r from-leaf-500 via-emerald-400 to-amber-300" style={{ width: `${(count / parcelHistory.length) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-soil-200 bg-white p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Dernières tendances</div>
              <div className="mt-4 space-y-3 text-sm text-soil-700">
                <div className="rounded-2xl bg-stone-50 px-4 py-3">Les analyses récentes montrent un flux orienté vers la surveillance et la confirmation plutôt qu’un profil stable unique.</div>
                <div className="rounded-2xl bg-stone-50 px-4 py-3">La parcelle la plus récente conserve un signal exploitable pour le concours: suivi, hiérarchisation et priorisation d’action.</div>
              </div>
            </div>
          </div>
        </Card>

        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <Card className="h-[420px]">
            <div className="mb-4 text-xl font-semibold text-soil-900">Comparaison validation / test</div>
            <ResponsiveContainer width="100%" height="88%">
              <BarChart data={compareData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(121,107,82,0.12)" />
                <XAxis dataKey="model" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="valid" fill="#319255" radius={[10, 10, 0, 0]} />
                <Bar dataKey="test" fill="#796b52" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card className="h-[420px]">
            <div className="mb-4 text-xl font-semibold text-soil-900">Lecture détaillée des labels</div>
            <ResponsiveContainer width="100%" height="88%">
              <LineChart data={nutrientTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(121,107,82,0.12)" />
                <XAxis dataKey="label" tickLine={false} axisLine={false} />
                <YAxis tickFormatter={(value) => `${value}%`} tickLine={false} axisLine={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="score" stroke="#205b3b" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {models.map((model) => (
            <Card key={model.family}>
              <div className="text-sm text-soil-500">{model.model_name}</div>
              <div className="mt-2 text-3xl font-semibold text-soil-900">{((model.hamming_accuracy ?? 0) * 100).toFixed(2)}%</div>
              <div className="mt-2 text-sm text-soil-600">Best guess from real project summaries and thresholds.</div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

import { AlertOctagon, AlertTriangle, ShieldCheck } from 'lucide-react';

import { AgricultureCard } from './agriculture-card';

export type ParcelTimelineItem = {
  id: string;
  dateLabel: string;
  score: number;
  confidence: number;
  status: 'stable' | 'watch' | 'priority';
  statusLabel: string;
  nutrientLabel: string;
  imageLabel: string;
};

type ParcelTimelineProps = {
  items: ParcelTimelineItem[];
};

export function ParcelTimeline({ items }: ParcelTimelineProps) {
  const statusConfig = {
    stable: {
      label: 'Stable',
      icon: ShieldCheck,
      tone: 'border-emerald-200 bg-emerald-50 text-emerald-800',
      dot: 'bg-emerald-500',
    },
    watch: {
      label: 'A surveiller',
      icon: AlertTriangle,
      tone: 'border-amber-200 bg-amber-50 text-amber-800',
      dot: 'bg-amber-500',
    },
    priority: {
      label: 'Prioritaire',
      icon: AlertOctagon,
      tone: 'border-rose-200 bg-rose-50 text-rose-800',
      dot: 'bg-rose-500',
    },
  } as const;

  return (
    <AgricultureCard className="space-y-6">
      <div>
        <div className="text-xs uppercase tracking-[0.2em] text-soil-500">Timeline parcelle</div>
        <div className="mt-2 text-2xl font-semibold text-soil-900">Progression des analyses</div>
      </div>
      {items.length ? (
        <div className="relative space-y-6">
          <div className="absolute left-4 top-2 h-[calc(100%-8px)] w-px bg-soil-200" />
          {items.map((item) => {
            const config = statusConfig[item.status];
            const StatusIcon = config.icon;
            return (
              <div key={item.id} className="relative pl-12">
                <div className={`absolute left-2 top-6 h-5 w-5 rounded-full border-4 border-white ${config.dot}`} />
                <div className="rounded-3xl border border-soil-200 bg-white p-4 shadow-sm">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="text-sm font-semibold text-soil-900">{item.dateLabel}</div>
                      <div className="mt-1 text-xs text-soil-500">{item.statusLabel}</div>
                      <div className="mt-2 text-xs uppercase tracking-[0.18em] text-soil-500">{item.imageLabel}</div>
                    </div>
                    <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${config.tone}`}>
                      <StatusIcon className="h-3.5 w-3.5" />
                      {config.label}
                    </div>
                  </div>

                  <div className="mt-4 grid gap-3 md:grid-cols-[120px_1fr]">
                    <div className="rounded-2xl border border-soil-100 bg-gradient-to-br from-soil-100 via-emerald-100 to-stone-50 p-3">
                      <div className="text-xs uppercase tracking-[0.18em] text-soil-500">Nutriment</div>
                      <div className="mt-2 text-sm font-semibold text-soil-900">{item.nutrientLabel}</div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-xs text-soil-500">
                        <span>Score sante</span>
                        <span className="font-semibold text-soil-900">{item.score}/100</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-soil-100">
                        <div className="h-full rounded-full bg-gradient-to-r from-leaf-500 via-emerald-400 to-emerald-300" style={{ width: `${item.score}%` }} />
                      </div>
                      <div className="flex items-center justify-between text-xs text-soil-500">
                        <span>Confiance</span>
                        <span className="font-semibold text-soil-900">{item.confidence}%</span>
                      </div>
                      <div className="h-1.5 overflow-hidden rounded-full bg-soil-100">
                        <div className="h-full rounded-full bg-gradient-to-r from-sky-400 via-cyan-400 to-teal-300" style={{ width: `${item.confidence}%` }} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="rounded-3xl border border-dashed border-soil-200 bg-soil-50 p-6 text-sm text-soil-600">
          Aucune analyse precedente disponible pour cette parcelle.
        </div>
      )}
    </AgricultureCard>
  );
}

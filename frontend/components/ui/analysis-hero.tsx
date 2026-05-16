import { CalendarDays, MapPinned, ShieldAlert, ShieldCheck, ShieldX } from 'lucide-react';

import { AgricultureCard } from './agriculture-card';

const statusTone = {
  bon: { icon: ShieldCheck, badge: 'bg-emerald-100 text-emerald-900' },
  acceptable: { icon: ShieldCheck, badge: 'bg-sky-100 text-sky-900' },
  'a surveiller': { icon: ShieldAlert, badge: 'bg-amber-100 text-amber-900' },
  critique: { icon: ShieldX, badge: 'bg-rose-100 text-rose-900' },
};

type AnalysisHeroProps = {
  parcelName: string;
  dateLabel: string;
  status: string;
  confidence: number;
  imageLabel?: string | null;
};

export function AnalysisHero({ parcelName, dateLabel, status, confidence, imageLabel }: AnalysisHeroProps) {
  const normalized = status.toLowerCase();
  const toneKey = normalized.includes('critique')
    ? 'critique'
    : normalized.includes('surveiller')
      ? 'a surveiller'
      : normalized.includes('acceptable')
        ? 'acceptable'
        : 'bon';
  const tone = statusTone[toneKey];
  const Icon = tone.icon;

  return (
    <AgricultureCard className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-soil-500">Analyse terrain</div>
          <div className="mt-2 text-3xl font-semibold text-soil-900">{parcelName}</div>
          <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-soil-600">
            <span className="inline-flex items-center gap-2"><CalendarDays className="h-4 w-4" />{dateLabel}</span>
            {imageLabel ? <span className="inline-flex items-center gap-2"><MapPinned className="h-4 w-4" />{imageLabel}</span> : null}
          </div>
        </div>
        <div className="space-y-2 text-right">
          <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${tone.badge}`}>
            <Icon className="h-4 w-4" />
            <span className="capitalize">{status}</span>
          </div>
          <div className="text-sm text-soil-600">Confiance analyse</div>
          <div className="text-3xl font-semibold text-soil-900">{confidence}%</div>
        </div>
      </div>
    </AgricultureCard>
  );
}

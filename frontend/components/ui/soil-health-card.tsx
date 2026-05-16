import { ShieldAlert, ShieldCheck, ShieldX } from 'lucide-react';

import { AgricultureCard } from './agriculture-card';
import { cn } from '@/lib/utils';

const toneMap = {
  bon: { icon: ShieldCheck, badge: 'bg-emerald-100 text-emerald-900', ring: 'ring-emerald-100' },
  acceptable: { icon: ShieldCheck, badge: 'bg-sky-100 text-sky-900', ring: 'ring-sky-100' },
  'a surveiller': { icon: ShieldAlert, badge: 'bg-amber-100 text-amber-900', ring: 'ring-amber-100' },
  critique: { icon: ShieldX, badge: 'bg-rose-100 text-rose-900', ring: 'ring-rose-100' },
};

type SoilHealthCardProps = {
  status: string;
  score: number;
  summary: string;
};

export function SoilHealthCard({ status, score, summary }: SoilHealthCardProps) {
  const normalized = status.toLowerCase();
  const toneKey = normalized.includes('critique')
    ? 'critique'
    : normalized.includes('surveiller')
      ? 'a surveiller'
      : normalized.includes('acceptable')
        ? 'acceptable'
        : 'bon';
  const tone = toneMap[toneKey];
  const Icon = tone.icon;

  return (
    <AgricultureCard className={cn('space-y-4 ring-1', tone.ring)}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-soil-500">Etat du sol</div>
          <div className="mt-2 flex items-center gap-2 text-2xl font-semibold text-soil-900">
            <Icon className="h-5 w-5" />
            <span className="capitalize">{status}</span>
          </div>
        </div>
        <div className={cn('rounded-full px-3 py-1 text-xs font-semibold', tone.badge)}>
          Indice sante: {score}%
        </div>
      </div>
      <p className="text-sm leading-6 text-soil-700">{summary}</p>
    </AgricultureCard>
  );
}

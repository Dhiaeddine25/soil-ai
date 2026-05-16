import { cn } from '@/lib/utils';
import { AgricultureCard } from './agriculture-card';

type NutrientStatusCardProps = {
  label: string;
  level: string;
  confidence: number;
  note: string;
};

export function NutrientStatusCard({ label, level, confidence, note }: NutrientStatusCardProps) {
  const clamped = Math.max(0, Math.min(100, confidence));
  const tone = level.toLowerCase().includes('faible') ? 'from-rose-400 via-rose-300 to-rose-200' : level.toLowerCase().includes('moyen') || level.toLowerCase().includes('surveiller') ? 'from-amber-400 via-amber-300 to-amber-200' : 'from-emerald-400 via-emerald-300 to-emerald-200';

  return (
    <AgricultureCard className="space-y-4">
      <div className="text-xs uppercase tracking-[0.2em] text-soil-500">{label}</div>
      <div className="text-2xl font-semibold text-soil-900">{level}</div>
      <div>
        <div className="flex items-center justify-between text-xs text-soil-500">
          <span>Confiance</span>
          <span>{clamped}%</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-soil-100">
          <div className={cn('h-full rounded-full bg-gradient-to-r', tone)} style={{ width: `${clamped}%` }} />
        </div>
      </div>
      <p className="text-sm leading-6 text-soil-700">{note}</p>
    </AgricultureCard>
  );
}

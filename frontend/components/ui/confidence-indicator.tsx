import { cn } from '@/lib/utils';

type ConfidenceIndicatorProps = {
  value: number;
  label?: string;
};

export function ConfidenceIndicator({ value, label = 'Niveau de confiance' }: ConfidenceIndicatorProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const tone = clamped >= 80 ? 'from-emerald-400 via-emerald-300 to-emerald-200' : clamped >= 60 ? 'from-amber-400 via-amber-300 to-amber-200' : 'from-rose-400 via-rose-300 to-rose-200';

  return (
    <div className="rounded-3xl border border-soil-200 bg-soil-50 p-5">
      <div className="flex items-center justify-between text-sm text-soil-600">
        <span>{label}</span>
        <span className="font-semibold text-soil-900">{clamped}%</span>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white">
        <div className={cn('h-full rounded-full bg-gradient-to-r', tone)} style={{ width: `${clamped}%` }} />
      </div>
    </div>
  );
}

import { AlertTriangle } from 'lucide-react';

import { AgricultureCard } from './agriculture-card';

type RefusalCardProps = {
  title: string;
  message: string;
  tips: string[];
  action?: React.ReactNode;
};

export function RefusalCard({ title, message, tips, action }: RefusalCardProps) {
  return (
    <AgricultureCard className="border-rose-200 bg-rose-50 text-rose-950">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-rose-100">
          <AlertTriangle className="h-5 w-5" />
        </span>
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-rose-600">Image non exploitable</div>
          <div className="mt-1 text-xl font-semibold">{title}</div>
        </div>
      </div>
      <p className="mt-4 text-sm leading-6 text-rose-900/80">{message}</p>
      <div className="mt-4 rounded-2xl border border-rose-200 bg-white/80 p-4 text-sm text-rose-900">
        <div className="text-xs uppercase tracking-[0.2em] text-rose-600">A faire</div>
        <ul className="mt-2 list-disc space-y-1 pl-4">
          {tips.map((tip) => (
            <li key={tip}>{tip}</li>
          ))}
        </ul>
      </div>
      {action ? <div className="mt-5 flex flex-wrap gap-3">{action}</div> : null}
    </AgricultureCard>
  );
}

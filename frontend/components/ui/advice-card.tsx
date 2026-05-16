import { Leaf } from 'lucide-react';

import { AgricultureCard } from './agriculture-card';

type AdviceCardProps = {
  title: string;
  body: string;
  disclaimer: string;
};

export function AdviceCard({ title, body, disclaimer }: AdviceCardProps) {
  return (
    <AgricultureCard className="space-y-3">
      <div className="flex items-center gap-2 text-sm text-soil-600">
        <Leaf className="h-4 w-4 text-leaf-600" />
        <span className="uppercase tracking-[0.2em]">Conseil terrain</span>
      </div>
      <div className="text-xl font-semibold text-soil-900">{title}</div>
      <p className="text-sm leading-6 text-soil-700">{body}</p>
      <p className="text-xs leading-5 text-soil-500">{disclaimer}</p>
    </AgricultureCard>
  );
}

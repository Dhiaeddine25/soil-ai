import { MapPinned } from 'lucide-react';

import { AgricultureCard } from './agriculture-card';

type ParcelMapProps = {
  title?: string;
  description?: string;
};

export function ParcelMap({ title = 'Localisation', description = 'Active la carte pour placer la parcelle.' }: ParcelMapProps) {
  return (
    <AgricultureCard className="flex items-center gap-4 bg-soil-50">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white">
        <MapPinned className="h-5 w-5 text-soil-700" />
      </div>
      <div>
        <div className="text-sm font-semibold text-soil-900">{title}</div>
        <div className="text-xs text-soil-600">{description}</div>
      </div>
    </AgricultureCard>
  );
}

import { Card } from '@/components/ui/card';

const stats = [
  ['Modèle de référence', 'EfficientNetV2L'],
  ['Hamming accuracy', '91.15%'],
  ['Usage visé', 'Pré-diagnostic'],
  ['Public cible', 'Terrain + incubateur'],
];

export function StatsRow() {
  return (
    <section className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl gap-4 md:grid-cols-4">
        {stats.map(([label, value]) => (
          <Card key={label} className="p-5">
            <div className="text-sm text-soil-500">{label}</div>
            <div className="mt-2 text-xl font-semibold text-soil-900">{value}</div>
          </Card>
        ))}
      </div>
    </section>
  );
}

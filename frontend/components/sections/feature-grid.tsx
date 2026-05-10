import { BarChart3, Layers3, UploadCloud, Users } from 'lucide-react';

import { Card } from '@/components/ui/card';

const features = [
  {
    icon: UploadCloud,
    title: 'Upload image',
    description: 'Dépose une image du sol pour générer une estimation rapide et orientative du profil NPK.',
  },
  {
    icon: BarChart3,
    title: 'Analytics crédibles',
    description: 'Expose les métriques réelles du projet: validation, test, comparaison des modèles et seuils.',
  },
  {
    icon: Layers3,
    title: 'Suivi parcellaire',
    description: 'Centralise les analyses, les interprétations et l’historique pour le suivi terrain.',
  },
  {
    icon: Users,
    title: 'Multi-public',
    description: 'Pensé pour agriculteurs, conseillers, coopératives, incubateurs et jurys techniques.',
  },
];

export function FeatureGrid() {
  return (
    <section className="px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title} className="h-full">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-leaf-50 text-leaf-700">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 text-xl font-semibold text-soil-900">{feature.title}</h3>
                <p className="mt-3 text-sm leading-6 text-soil-600">{feature.description}</p>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}

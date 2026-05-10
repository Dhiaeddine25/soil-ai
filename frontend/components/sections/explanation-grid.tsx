import { BadgeCheck, Camera, ClipboardList, ShieldAlert } from 'lucide-react';

import { Card } from '@/components/ui/card';

const steps = [
  { icon: Camera, title: 'Capture image', description: 'L’utilisateur prend ou importe une image du sol depuis le terrain.' },
  { icon: BadgeCheck, title: 'IA de pré-estimation', description: 'Le moteur applique le meilleur modèle disponible ou un mode mock réaliste.' },
  { icon: ClipboardList, title: 'Interprétation prudente', description: 'La sortie est traduite en niveaux NPK lisibles et en recommandation terrain.' },
  { icon: ShieldAlert, title: 'Confirmation si nécessaire', description: 'Le laboratoire reste la référence quand une confirmation est nécessaire.' },
];

export function ExplanationGrid() {
  return (
    <section className="px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <Card key={step.title} className="relative">
                <div className="absolute right-5 top-5 text-4xl font-semibold text-soil-200">0{index + 1}</div>
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-soil-900 text-white">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 text-xl font-semibold text-soil-900">{step.title}</h3>
                <p className="mt-3 text-sm leading-6 text-soil-600">{step.description}</p>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}

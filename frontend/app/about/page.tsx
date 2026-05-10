import { Card } from '@/components/ui/card';
import { SectionTitle } from '@/components/sections/section-title';

const values = [
  ['Mission', 'Apporter un pré-diagnostic NPK simple, rapide et crédible pour mieux orienter la décision.'],
  ['Vision', 'Construire une brique agritech incubable au service du terrain, de la démonstration et du suivi.'],
  ['Impact', 'Réduire le délai entre observation et action, sans remplacer le laboratoire.'],
  ['Durabilité', 'Promouvoir une gestion des apports plus contextualisée et plus prudente.'],
];

export default function AboutPage() {
  return (
    <div className="px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <SectionTitle
          eyebrow="Vision"
          title="Une base produit sérieuse pour mémoire, startup et terrain"
          description="La narration produit doit rester honnête: un outil d’aide à la décision, pas un substitut total au laboratoire."
        />
        <div className="grid gap-5 md:grid-cols-2">
          {values.map(([title, description]) => (
            <Card key={title}>
              <div className="text-xl font-semibold text-soil-900">{title}</div>
              <p className="mt-3 text-sm leading-6 text-soil-600">{description}</p>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

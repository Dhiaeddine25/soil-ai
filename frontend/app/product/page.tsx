import { Card } from '@/components/ui/card';
import { SectionTitle } from '@/components/sections/section-title';
import { Button } from '@/components/ui/button';

const items = [
  'Upload image du sol',
  'Estimation NPK',
  'Score de confiance',
  'Historique d’analyses',
  'Suivi de parcelles',
  'Aide à la décision',
];

export default function ProductPage() {
  return (
    <div className="px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <SectionTitle
          eyebrow="Produit"
          title="Des fonctionnalités pensées pour une démonstration crédible"
          description="La page produit met en avant les blocs réellement utiles pour un pilote: upload, prédiction, confiance, historique et suivi parcellaire."
        />

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => (
            <Card key={item}>
              <div className="text-lg font-semibold text-soil-900">{item}</div>
              <p className="mt-3 text-sm leading-6 text-soil-600">
                Composant prêt à être relié au backend pour une expérience produit stable et orientée usage terrain.
              </p>
            </Card>
          ))}
        </div>

        <Card className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-sm uppercase tracking-[0.2em] text-soil-500">Mise en avant</div>
            <div className="mt-2 text-2xl font-semibold text-soil-900">Pré-diagnostic rapide, interprétation prudente, suivi possible</div>
          </div>
          <Button>Planifier un pilote</Button>
        </Card>
      </div>
    </div>
  );
}

import { SectionTitle } from '@/components/sections/section-title';
import { ExplanationGrid } from '@/components/sections/explanation-grid';

export default function HowItWorksPage() {
  return (
    <div className="space-y-8">
      <div className="px-4 pt-12 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <SectionTitle
            eyebrow="Méthode"
            title="Comment la plateforme travaille"
            description="Image du sol, traitement IA, estimation NPK, niveau de confiance, interprétation et recommandation prudente."
          />
        </div>
      </div>
      <ExplanationGrid />
    </div>
  );
}

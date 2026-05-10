import { AnalyticsPanel } from '@/components/sections/analytics-panel';
import { SectionTitle } from '@/components/sections/section-title';
import { getResultsSummary } from '@/lib/api';
import { resultsSummary } from '@/lib/mock';

async function loadResults() {
  try {
    return await getResultsSummary();
  } catch {
    return resultsSummary;
  }
}

export default async function AnalyticsPage() {
  const results = await loadResults();

  return (
    <div className="space-y-8">
      <div className="px-4 pt-12 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <SectionTitle
            eyebrow="Analytics"
            title="Résultats des modèles et comparaison scientifique"
            description="Cette page expose les performances réelles tirées de tes artefacts: validation, test, meilleur modèle, seuils et tendances des labels."
          />
        </div>
      </div>
      <AnalyticsPanel results={results} />
    </div>
  );
}

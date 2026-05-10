import { Card } from '@/components/ui/card';
import { formatPercent } from '@/lib/utils';
import { resultsSummary } from '@/lib/mock';
import { getNutrientLevelLabel, getNutrientName } from '@/lib/soil-insights';

export function ResultsPreview() {
  const model = resultsSummary.best_model;

  return (
    <section className="px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <div className="text-sm uppercase tracking-[0.2em] text-soil-500">Résultats du projet</div>
          <h3 className="mt-3 text-2xl font-semibold text-soil-900">Le meilleur candidat actuellement mis en avant</h3>
          <p className="mt-3 text-sm leading-6 text-soil-600">
            Le catalogue de résultats montre EfficientNetV2L comme modèle de référence, avec DenseNet201 en comparaison scientifique.
          </p>
          <div className="mt-6 rounded-2xl border border-soil-100 bg-soil-50 p-5">
            <div className="flex items-center justify-between">
              <span className="font-medium text-soil-700">{model.model_name}</span>
              <span className="rounded-full bg-leaf-100 px-3 py-1 text-sm font-semibold text-leaf-800">Best model</span>
            </div>
            <div className="mt-4 text-4xl font-semibold text-soil-900">{formatPercent(model.hamming_accuracy ?? 0)}</div>
            <div className="mt-2 text-sm text-soil-600">Hamming accuracy validé sur les artefacts du projet.</div>
          </div>
        </Card>

        <Card>
          <div className="grid gap-4 sm:grid-cols-3">
            {['K', 'N', 'P'].map((nutrient) => (
              <div key={nutrient} className="rounded-2xl border border-soil-100 bg-white p-4">
                <div className="text-sm text-soil-500">{getNutrientName(nutrient as 'K' | 'N' | 'P')}</div>
                <div className="mt-2 text-2xl font-semibold text-soil-900">{getNutrientLevelLabel(nutrient === 'K' ? 'K1' : nutrient === 'N' ? 'N1' : 'P0')}</div>
                <div className="mt-1 text-sm text-soil-600">Exemple de sortie mock réaliste</div>
              </div>
            ))}
          </div>
          <div className="mt-5 space-y-3">
            {resultsSummary.baseline_notes.map((note) => (
              <div key={note} className="rounded-2xl border border-soil-100 bg-soil-50 p-4 text-sm text-soil-700">
                {note}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </section>
  );
}

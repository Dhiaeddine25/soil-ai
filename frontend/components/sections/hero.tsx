import Link from 'next/link';
import { ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export function Hero() {
  return (
    <section className="relative overflow-hidden px-4 pt-10 sm:px-6 lg:px-8 lg:pt-16">
      <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div className="relative z-10">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-leaf-200 bg-white/70 px-4 py-2 text-sm text-soil-700 shadow-sm">
            <Sparkles className="h-4 w-4 text-leaf-600" />
            Pré-diagnostic NPK à partir d’images du sol
          </div>
          <h1 className="max-w-4xl text-5xl font-semibold tracking-tight text-soil-900 sm:text-6xl lg:text-7xl">
            Une plateforme agritech crédible pour estimer le NPK, suivre les parcelles et mieux décider.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-soil-600 sm:text-xl">
            SoilAI transforme tes modèles déjà entraînés en une expérience produit sérieuse pour le mémoire, la démonstration,
            l’incubation et les premiers usages terrain. L’outil donne une estimation rapide et orientative, sans se substituer au laboratoire.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/dashboard">
              <Button>
                Ouvrir le dashboard
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/analytics">
              <Button variant="ghost">Voir les résultats modèles</Button>
            </Link>
          </div>
          <div className="mt-8 flex flex-wrap gap-4 text-sm text-soil-600">
            <div className="flex items-center gap-2 rounded-full bg-white/70 px-4 py-2 shadow-sm">
              <ShieldCheck className="h-4 w-4 text-leaf-600" />
              Pré-diagnostic, pas diagnostic final
            </div>
            <div className="flex items-center gap-2 rounded-full bg-white/70 px-4 py-2 shadow-sm">
              <ShieldCheck className="h-4 w-4 text-leaf-600" />
              Résultats fondés sur tes vrais artefacts
            </div>
          </div>
        </div>

        <Card className="relative overflow-hidden border border-white/70 bg-soil-900 text-white shadow-soft">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(91,167,104,0.35),_transparent_40%)]" />
          <div className="relative space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-soil-200">Analyse active</p>
                <h3 className="text-2xl font-semibold">Parcelle A12</h3>
              </div>
              <div className="rounded-full bg-leaf-500/20 px-3 py-1 text-sm font-medium text-leaf-200">EfficientNetV2L</div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[
                ['Azote', 'N1', '0.91'],
                ['Phosphore', 'P0', '0.88'],
                ['Potassium', 'K1', '0.87'],
              ].map(([label, value, confidence]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/6 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-soil-300">{label}</div>
                  <div className="mt-2 text-2xl font-semibold">{value}</div>
                  <div className="mt-1 text-sm text-soil-300">Confiance {confidence}</div>
                </div>
              ))}
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/8 p-4 text-sm leading-6 text-soil-100">
              Résultat indicatif robuste. Surveillance recommandée et confirmation laboratoire conseillée selon le niveau d’enjeu.
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
}

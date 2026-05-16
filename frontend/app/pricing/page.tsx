"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function PricingPage() {
  return (
    <section className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="mb-6 text-3xl font-bold text-center text-soil-900">
          Tarifs
        </h1>
        <p className="mb-8 text-center text-soil-600">
          Choisissez le plan qui convient à vos besoins agricoles
        </p>

        <div className="grid gap-6 sm:grid-cols-1 lg:grid-cols-3">
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-center text-soil-900 mb-4">
              Offre Pilote
            </h2>
            <p className="text-center text-soil-600">
              Pour les fermes pilotes et démonstrations
            </p>
            <ul className="mt-4 space-y-2 text-left text-soil-600">
              <li>Nombre limité d'analyses</li>
              <li>Nombre limité de parcelles</li>
              <li>Exports basiques</li>
              <li>Support simple</li>
            </ul>
            <Link
              href="#"
              className="w-full mt-6 bg-leaf-600 text-white hover:bg-leaf-700 inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-leaf-400 focus:ring-offset-2"
            >
              Commencer l'essai
            </Link>
          </Card>

          <Card className="p-6 border-2 border-leaf-200 bg-leaf-50">
            <h2 className="text-xl font-semibold text-center text-white mb-4">
              Offre Pro
            </h2>
            <p className="text-center text-white/90">
              Pour les coopératives et conseillers agronomes
            </p>
            <ul className="mt-4 space-y-2 text-left text-white/90">
              <li>Multi-utilisateurs</li>
              <li>Multi-parcelles</li>
              <li>Dashboard avancé</li>
              <li>Exports premium</li>
              <li>Historique complet</li>
              <li>Analytics</li>
            </ul>
            <Link
              href="#"
              className="w-full mt-6 bg-white/20 text-white hover:bg-white/30 inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2"
            >
              Commencer l'essai
            </Link>
          </Card>

          <Card className="p-6">
            <h2 className="text-xl font-semibold text-center text-soil-900 mb-4">
              Offre API / Entreprise
            </h2>
            <p className="text-center text-soil-600">
              Pour les intégrations et plateformes agricoles
            </p>
            <ul className="mt-4 space-y-2 text-left text-soil-600">
              <li>Accès API</li>
              <li>Intégration externe</li>
              <li>Analytics avancés</li>
              <li>Support entreprise</li>
            </ul>
            <Link
              href="#"
              className="w-full mt-6 border border-leaf-200 text-leaf-600 hover:border-leaf-700 inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-leaf-400 focus:ring-offset-2"
            >
              Contacter les ventes
            </Link>
          </Card>
        </div>

        <div className="mt-10 text-center text-soil-500">
          <p>
            Tous les prix sont en HT et facturés annuellement. Des remises sont disponibles pour les engagements de plusieurs années.
          </p>
        </div>
      </div>
    </section>
  );
}
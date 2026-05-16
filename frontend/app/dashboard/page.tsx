"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';
import { useAuth } from '@/components/auth/auth-provider';
import { useEffect, useState } from 'react';
import { listParcels, getHistory } from '@/lib/api';

export default function DashboardPage() {
  const { messages } = useI18n();
  const { user, token, loading: authLoading } = useAuth();
  const [parcels, setParcels] = useState<Array<any>>([]);
  const [history, setHistory] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user || !token) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    // Fetch parcels
    listParcels(token)
      .then((data) => {
        setParcels(data);
      })
      .catch((err) => {
        console.error('Failed to fetch parcels:', err);
        setParcels([]);
      });

    // Fetch history
    getHistory(user.id, token)
      .then((res) => {
        setHistory(res.entries ?? []);
      })
      .catch((err) => {
        console.error('Failed to fetch history:', err);
        setHistory([]);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [user, token]);

  if (loading) {
    return (
      <section className="px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-leaf-600"></div>
            <p className="mt-4 text-sm text-soil-600">Chargement des données...</p>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="bg-amber-50 border-l-4 border-amber-200 p-4">
            <p className="text-sm text-amber-800">
              {error}
            </p>
          </div>
        </div>
      </section>
    );
  }

  const totalAnalyses = history.length;
  const averageScore =
    totalAnalyses > 0
      ? Math.round(
          history.reduce((sum, entry) => sum + (entry.score || 0), 0) /
            totalAnalyses
        )
      : 0;

  return (
    <section className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-soil-900">
            Tableau de bord
          </h1>
          <p className="text-sm text-soil-600">
            Bonjour, {user?.full_name ?? user?.email ?? 'Utilisateur'}
          </p>
        </div>
        <div className="grid gap-6">
          {/* Stats cards */}
          <div className="grid gap-4 sm:grid-cols-3">
            <Card className="bg-white/5 backdrop-blur-sm">
              <div className="flex items-center justify-between p-6">
                <div>
                  <h3 className="text-sm font-medium text-soil-500">
                    Parcelles suivies
                  </h3>
                  <p className="text-2xl font-bold text-soil-900">
                    {parcels.length}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-leaf-100 text-leaf-800">
                  <span className="material-icons">eco</span>
                </div>
              </div>
            </Card>
            <Card className="bg-white/5 backdrop-blur-sm">
              <div className="flex items-center justify-between p-6">
                <div>
                  <h3 className="text-sm font-medium text-soil-500">
                    Analyses totales
                  </h3>
                  <p className="text-2xl font-bold text-soil-900">
                    {totalAnalyses}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-leaf-100 text-leaf-800">
                  <span className="material-icons">analytics</span>
                </div>
              </div>
            </Card>
            <Card className="bg-white/5 backdrop-blur-sm">
              <div className="flex items-center justify-between p-6">
                <div>
                  <h3 className="text-sm font-medium text-soil-500">
                    Score moyen du sol
                  </h3>
                  <p className="text-2xl font-bold text-soil-900">
                    {averageScore}
                  </p>
                  <p className="text-xs text-soil-500">
                    Sur 100
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-leaf-100 text-leaf-800">
                  <span className="material-icons">local_florist</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Recent analyses */}
          <Card className="bg-white/5 backdrop-blur-sm">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-soil-900 mb-4">
                Analyses récentes
              </h2>
              {totalAnalyses === 0 ? (
                <p className="text-sm text-soil-600 text-center py-8">
                  Aucune analyse disponible. Commencez par analyser un sol.
                </p>
              ) : (
                <div className="space-y-4">
                  {history
                    .slice(0, 3)
                    .map((entry) => (
                      <div
                        key={entry.analysis_id}
                        className="flex items-center justify-between p-4 bg-white/10 rounded-lg"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-soil-900">
                            {entry.parcel?.name || 'Parcelle inconnue'}
                          </p>
                          <p className="text-xs text-soil-500 truncate">
                            {new Date(entry.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right flex-items-baseline">
                          <span className="text-xl font-bold text-soil-900">
                            {entry.score || 0}
                          </span>
                          <span className="text-xs text-soil-500 ml-2">
                            /100
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
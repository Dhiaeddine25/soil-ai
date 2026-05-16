'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';
import type { HistoryEntry } from '@/lib/types';
import { getSoilScore } from '@/lib/soil-insights';

interface MobileHistoryProps {
  onAnalysisSelect: (analysis: HistoryEntry) => void;
}

export function MobileHistory({ onAnalysisSelect }: MobileHistoryProps) {
  const { messages } = useI18n();
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // In a real app, we would fetch from an API endpoint like `/api/history`
  // For now, we'll simulate with an empty array or mock data
  // We'll assume there's a hook or service to fetch history
  // Since we don't have the exact API, we'll leave it as empty for now
  // and show a message if no history.
  // We'll also add a refresh button to simulate fetching.

  const fetchHistory = async () => {
    setLoading(true);
    try {
      // In a real app, we would fetch from an API endpoint like `/api/history`
      // For now, we'll simulate with an empty array or mock data
      // We'll assume there's a hook or service to fetch history
      // Since we don't have the exact API, we'll leave it as empty for now
      // and show a message if no history.
      // Mock data for demonstration - remove in production
      /*
      const mockHistory: HistoryEntry[] = [
        {
          analysis_id: '1',
          user_id: 'user1',
          parcel_id: 'parcel1',
          image_name: 'soil1.jpg',
          prediction: { K_level: 'K1', N_level: 'N1', P_level: 'P1' },
          confidence: 0.85,
          score: 75,
          timestamp: new Date().toISOString(),
          status: 'ok',
          interpretation: 'Lecture utile, à confirmer selon le contexte parcellaire.',
          recommendation_message: 'Maintenir les pratiques agricoles actuelles.',
          agronomic_advice: {
            nitrogen: { advice: 'Niveau d\'azote adapté.', soil_status: 'ok' },
            phosphorus: { advice: 'Niveau de phosphore adequate.', soil_status: 'ok' },
            potassium: { advice: 'Niveau de potassium adequate.', soil_status: 'ok' },
            global_advice: { warning: 'Conseil indicatif basé sur une analyse d’image.' }
          }
        }
      ];
      setHistory(mockHistory);
      */
      // For now, we'll just set an empty array and show the message.
      setHistory([]);
    } catch (err) {
      setError('Impossible de charger l\'historique.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch history on mount
  // useEffect(() => {
  //   fetchHistory();
  // }, []);

  // For now, we'll fetch manually via a button to avoid extra dependencies in this example.
  // In a real app, we would use useEffect.

  if (loading) {
    return (
       <Card className="space-y-4">
         <div className="text-center py-8">
           <svg className="h-8 w-8 text-soil-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2 2 4 4 4h4c2 0 4-2 4-4V7m-9-4h2m2 2h2m-2 4h2m2 2h2m2-4h2m2 2h2" />
           </svg>
           <p className="text-sm text-soil-600">Chargement de l'historique...</p>
         </div>
       </Card>
    );
  }

  if (error) {
    return (
      <Card className="space-y-4">
        <div className="text-center py-8">
          <svg className="h-8 w-8 text-amber-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.956c1.54 0 2.502-1.667 1.732-3L13.732 9c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-sm text-amber-900">{error}</p>
          <Button
            onClick={fetchHistory}
            variant="secondary"
            className="mt-4"
          >
            Réessayer
          </Button>
        </div>
      </Card>
    );
  }

  if (history.length === 0) {
    return (
      <Card className="space-y-4">
        <div className="text-center py-8">
          <svg className="h-8 w-8 text-soil-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m2 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-soil-600">Aucune analyse effectuée pour le moment.</p>
          <Button
            onClick={fetchHistory}
            variant="secondary"
            className="mt-4"
          >
            Actualiser
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="space-y-4">
      <div className="flex justify-between items-center pb-3 border-b border-soil-100">
        <h3 className="text-lg font-semibold text-soil-900">
          Historique des analyses
        </h3>
        <Button
          onClick={fetchHistory}
          variant="secondary"
        >
          Actualiser
        </Button>
      </div>

      <div className="space-y-3">
        {history.slice(0, 5).map((analysis) => (
          <div
            key={analysis.analysis_id}
            onClick={() => onAnalysisSelect(analysis)}
            className="cursor-pointer border rounded-xl p-4 hover:bg-leaf-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="font-medium text-soil-900">
                  Parcelle: {analysis.parcel_id ?? 'Inconnue'}
                  {analysis.image_name ? (
                    <span className="ml-2 text-xs text-soil-500">
                      ({analysis.image_name})
                    </span>
                  ) : null}
                </p>
                <p className="text-sm text-soil-600 truncate">
                  {new Date(analysis.created_at ?? '').toLocaleDateString()} {new Date(analysis.created_at ?? '').toLocaleTimeString()}
                </p>
              </div>
              <div className="text-right flex-1 items-end">
                <div className="text-xl font-bold">
                  {analysis.score ?? 0}
                </div>
                <div className="text-xs text-soil-500">
                  /100
                </div>
              </div>
            </div>
          </div>
        ))}
        {history.length > 5 && (
          <div className="text-center text-sm text-soil-500">
            Et {history.length - 5} autres analyses...
          </div>
        )}
      </div>
    </Card>
  );
}

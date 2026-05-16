import type { HistoryEntry } from './types';
import { getSoilScore } from './soil-insights';

export type ParcelAnalyticsSeed = {
  parcelId?: string | null;
  seasonalTrend: Array<{ season: string; score: number; trend: 'up' | 'down' | 'stable' }>;
  alerts: Array<{ id: string; label: string; priority: 'low' | 'medium' | 'high' }>;
};

export function buildParcelAnalyticsSeed(entries: HistoryEntry[]): ParcelAnalyticsSeed {
  const ordered = [...entries]
    .filter((entry) => entry.prediction)
    .sort((left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime());

  const seasonalTrend = ordered.map((entry, index) => {
    const score = getSoilScore(entry.prediction).score;
    const previousScore = index > 0 ? getSoilScore(ordered[index - 1].prediction).score : score;
    const trend: ParcelAnalyticsSeed['seasonalTrend'][number]['trend'] = score > previousScore ? 'up' : score < previousScore ? 'down' : 'stable';
    const date = new Date(entry.created_at);
    const seasonLabel = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    return { season: seasonLabel, score, trend };
  });

  return {
    parcelId: entries[0]?.parcel_id ?? null,
    seasonalTrend,
    alerts: [],
  };
}

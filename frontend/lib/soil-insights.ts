import type { HistoryEntry, PredictionResponse } from './types';

const priorityRank: Record<'high' | 'moderate' | 'low', number> = {
  high: 0,
  moderate: 1,
  low: 2,
};

const nutrientClassRank: Record<string, number> = {
  K0: 0,
  K1: 1,
  K2: 2,
  N0: 0,
  N1: 1,
  N2: 2,
  P0: 0,
  P1: 1,
};

const nutrientNames: Record<'K' | 'N' | 'P', string> = {
  K: 'Potassium',
  N: 'Azote',
  P: 'Phosphore',
};

const priorityLabels: Record<'high' | 'moderate' | 'low', string> = {
  high: 'élevée',
  moderate: 'modérée',
  low: 'faible',
};

const nutrientLevelLabels: Record<string, string> = {
  K0: 'faible',
  N0: 'faible',
  P0: 'faible',
  K1: 'moyen',
  N1: 'moyen',
  P1: 'acceptable',
  K2: 'bon',
  N2: 'bon',
};

export function getNutrientName(nutrient: 'K' | 'N' | 'P') {
  return nutrientNames[nutrient];
}

export function getPriorityLabel(priority: 'high' | 'moderate' | 'low') {
  return priorityLabels[priority];
}

export function getNutrientLevelLabel(level?: string | null) {
  if (!level) {
    return 'non renseigné';
  }

  return nutrientLevelLabels[level] ?? 'bon';
}

export function getSoilStatusLabel(status?: string | null) {
  if (!status) {
    return 'à surveiller';
  }

  if (status === 'profil rassurant' || status === 'bon') {
    return 'bon';
  }

  if (status === 'suivi conseillé' || status === 'acceptable') {
    return 'acceptable';
  }

  if (status === 'surveillance prioritaire' || status === 'à surveiller') {
    return 'à surveiller';
  }

  if (status === 'action prioritaire' || status === 'critique') {
    return 'critique';
  }

  return status;
}

export function getFocusLabel(focus?: string | null) {
  if (!focus) {
    return 'phosphore';
  }

  return nutrientNames[focus as 'K' | 'N' | 'P']?.toLowerCase() ?? focus.toLowerCase();
}

export function getPredictionStatusLabel(status?: string | null) {
  if (!status) {
    return 'Analyse disponible';
  }

  if (status === 'ok') {
    return 'Analyse prête';
  }

  if (status === 'image_non_exploitable') {
    return 'Image non exploitable';
  }

  if (status === 'prediction_incertaine') {
    return 'Résultat incertain';
  }

  if (status === 'confirmation_recommandee') {
    return 'Confirmation recommandée';
  }

  return status.replaceAll('_', ' ');
}

export function getSoilScore(prediction?: PredictionResponse | null) {
  const advice = prediction?.agronomic_advice?.global_advice;
  return {
    score: prediction?.score ?? advice?.soil_score ?? 0,
    level: advice?.soil_level ?? 'critique',
    status: getSoilStatusLabel(advice?.soil_status),
    focus: advice?.priority_focus ?? 'P',
    summary: advice?.summary ?? 'Analyse non disponible.',
  };
}

export function getSortedNutrientAdvice(prediction?: PredictionResponse | null) {
  const advice = prediction?.agronomic_advice;
  if (!advice) {
    return [];
  }

  return [advice.potassium, advice.nitrogen, advice.phosphorus].sort(
    (left, right) => priorityRank[left.priority] - priorityRank[right.priority],
  );
}

export function compareNutrientLevel(previousLevel?: string | null, currentLevel?: string | null) {
  if (!previousLevel || !currentLevel) {
    return { trend: 'stable' as const, delta: 0 };
  }

  const previousRank = nutrientClassRank[previousLevel] ?? 0;
  const currentRank = nutrientClassRank[currentLevel] ?? 0;
  const delta = currentRank - previousRank;

  if (delta > 0) {
    return { trend: 'amélioration' as const, delta };
  }

  if (delta < 0) {
    return { trend: 'baisse' as const, delta };
  }

  return { trend: 'stable' as const, delta: 0 };
}

export function comparePredictions(previous?: PredictionResponse | null, current?: PredictionResponse | null) {
  const previousScore = getSoilScore(previous).score;
  const currentScore = getSoilScore(current).score;
  const scoreDelta = currentScore - previousScore;

  return {
    score: scoreDelta > 0 ? 'amélioration' : scoreDelta < 0 ? 'baisse' : 'stable',
    scoreDelta,
    K: compareNutrientLevel(previous?.prediction?.K_level, current?.prediction?.K_level),
    N: compareNutrientLevel(previous?.prediction?.N_level, current?.prediction?.N_level),
    P: compareNutrientLevel(previous?.prediction?.P_level, current?.prediction?.P_level),
  };
}

export function buildTimeline(entries: HistoryEntry[]) {
  return [...entries]
    .filter((entry) => entry.prediction)
    .sort((left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime())
    .map((entry) => ({
      entry,
      ...getSoilScore(entry.prediction),
    }));
}

export function buildWatchlist(entries: HistoryEntry[]) {
  return [...entries]
    .filter((entry) => {
      const score = getSoilScore(entry.prediction).score;
      const status = entry.prediction?.status;
      return score < 60 || status === 'prediction_incertaine' || status === 'confirmation_recommandee' || status === 'image_non_exploitable';
    })
    .sort((left, right) => {
      const leftScore = getSoilScore(left.prediction).score;
      const rightScore = getSoilScore(right.prediction).score;
      return leftScore - rightScore || new Date(right.created_at).getTime() - new Date(left.created_at).getTime();
    });
}
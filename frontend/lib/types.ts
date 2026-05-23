export type NutrientLevel = 'K0' | 'K1' | 'K2' | 'N0' | 'N1' | 'N2' | 'P0' | 'P1';

export interface ModelSummary {
  model_name: string;
  family: string;
  hamming_accuracy?: number | null;
  macro_f1_global?: number | null;
  per_label_accuracy: Record<string, number>;
  thresholds: Record<string, number>;
  sources: Record<string, string>;
}

export interface ResultsSummaryResponse {
  best_model: ModelSummary;
  models: ModelSummary[];
  baseline_notes: string[];
}

export interface PredictionResponse {
  analysis_id?: string | null;
  model_name: string;
  npk_prediction?: {
    K_level: 'K0' | 'K1' | 'K2';
    N_level: 'N0' | 'N1' | 'N2';
    P_level: 'P0' | 'P1';
  } | null;
  prediction?: {
    K_level: 'K0' | 'K1' | 'K2';
    N_level: 'N0' | 'N1' | 'N2';
    P_level: 'P0' | 'P1';
  } | null;
  confidence?: number | null;
  status: 'image_non_exploitable' | 'prediction_incertaine' | 'confirmation_recommandee' | 'ok';
  can_trust_result: boolean;
  quality_check: QualityCheck;
  confidence_details?: ConfidenceDetails | null;
  interpretation: string;
  recommendation: string;
  agronomic_advice: AgronomicAdvice;
  nitrogen?: NutrientPredictionDetail | null;
  phosphorus?: NutrientPredictionDetail | null;
  potassium?: NutrientPredictionDetail | null;
  field_advice?: string | null;
  field_disclaimer?: string | null;
  soil_health_score?: number | null;
  image_quality?: {
    image_quality_score?: number | null;
    warning?: 'low_image_quality' | string | null;
    recommendations?: string[];
  } | null;
  uncertainty_metrics?: Record<string, Record<string, unknown>>;
  debug?: PredictionDebug | null;
  score_breakdown?: Record<string, unknown> | null;
  score?: number | null;
  refused?: boolean;
  refusal_reason?: string | null;
  image_name?: string | null;
  image_url?: string | null;
  warning_message: string;
  recommendation_message: string;
  warning?: 'low_image_quality' | string | null;
  recommendations?: string[];
  image_quality_score?: number | null;
  is_mock: boolean;
  timestamp: string;
  source: string;
  model_status: string;
  probabilities: Record<string, number>;
}

export interface NutrientPredictionDetail {
  class: string;
  confidence: number;
  probabilities: number[];
  raw_probabilities?: number[] | null;
  calibrated_probabilities?: number[] | null;
  interpretation: string;
  signal_score: number;
  raw_entropy?: number | null;
  calibrated_entropy?: number | null;
  entropy_baseline?: number | null;
  entropy_ratio?: number | null;
  calibration_factor?: number | null;
  uncertainty_adjustment?: number | null;
  softened?: boolean | null;
  variance_index?: number | null;
  uncertainty_score?: number | null;
}

export interface PredictionDebug {
  calibration_mode?: string;
  calibration_factor?: number;
  temperature_proxy?: number;
  raw_probabilities?: Record<string, number>;
  calibrated_probabilities?: Record<string, number>;
  entropy_before?: Record<string, number>;
  entropy_after?: Record<string, number>;
  entropy_baseline?: Record<string, number>;
  uncertainty_adjustment?: Record<string, number>;
  models?: Array<Record<string, unknown>>;
}

export interface QualityCheck {
  valid: boolean;
  status: 'ok' | 'image_non_exploitable';
  width?: number | null;
  height?: number | null;
  brightness?: number | null;
  contrast?: number | null;
  sharpness?: number | null;
  issues: string[];
}

export interface ConfidenceDetails {
  max_prob: number;
  second_prob: number;
  margin: number;
  top_label?: string | null;
  top_group?: string | null;
}

export interface NutrientAdvice {
  nutrient: 'K' | 'N' | 'P';
  level: string;
  priority: 'high' | 'moderate' | 'low';
  advice: string;
  soil_status: string;
  summary: string;
  warning: string;
}

export interface GlobalAgronomicAdvice {
  soil_score: number;
  soil_level: 'bon' | 'acceptable' | 'à surveiller' | 'critique';
  soil_status: string;
  priority_focus: 'K' | 'N' | 'P';
  priority_summary: string;
  summary: string;
  warning: string;
}

export interface AgronomicAdvice {
  potassium: NutrientAdvice;
  nitrogen: NutrientAdvice;
  phosphorus: NutrientAdvice;
  global_advice: GlobalAgronomicAdvice;
}

export interface HistoryEntry {
  id?: string | null;
  user_id: string;
  parcel_id?: string | null;
  parcel?: ParcelPublic | null;
  image_name?: string | null;
  image_path?: string | null;
  image_url?: string | null;
  analysis_id: string;
  created_at: string;
  predictions?: {
    K_level: 'K0' | 'K1' | 'K2';
    N_level: 'N0' | 'N1' | 'N2';
    P_level: 'P0' | 'P1';
  } | null;
  probabilities?: Record<string, number>;
  confidence?: number;
  score?: number;
  advice?: string | null;
  refused?: boolean;
  refusal_reason?: string | null;
  prediction: PredictionResponse | null;
}

export interface HistoryListResponse {
  user_id: string;
  total: number;
  entries: HistoryEntry[];
}

export interface UserPublic {
  id: string;
  email: string;
  full_name?: string | null;
  created_at: string;
}

export interface ParcelPublic {
  id: string;
  user_id: string;
  name: string;
  location?: string | null;
  region?: string | null;
  area_ha?: number | null;
  crop?: string | null;
  notes?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  created_at: string;
}

export interface AuthSession {
  access_token: string;
  token_type: string;
  user: UserPublic;
}

export interface AuthState {
  user: UserPublic | null;
  loading: boolean;
  isAuthenticated: boolean;
  status: 'loading' | 'authenticated' | 'unauthenticated' | 'error';
  error?: string | null;
}

export interface ModelInfo {
  active_model: {
    model_name: string;
    family: string;
    status: string;
    version: string;
    description: string;
    image_size: number;
    labels: string[];
    performance: {
      hamming_accuracy?: number | null;
      macro_f1_global?: number | null;
      per_label_accuracy: Record<string, number>;
      thresholds: Record<string, number>;
    };
    artifact_paths: Record<string, string>;
  };
  available_models: Array<ModelInfo['active_model']>;
  server_time: string;
  note: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string | null;
}

export interface ParcelCreatePayload {
  name: string;
  location?: string | null;
  region?: string | null;
  area_ha?: number | null;
  crop?: string | null;
  notes?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface ParcelUpdatePayload {
  name?: string | null;
  location?: string | null;
  region?: string | null;
  area_ha?: number | null;
  crop?: string | null;
  notes?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

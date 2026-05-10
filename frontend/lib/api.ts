import type {
  AuthSession,
  HistoryEntry,
  HistoryListResponse,
  LoginPayload,
  ModelInfo,
  ParcelCreatePayload,
  ParcelPublic,
  ParcelUpdatePayload,
  PredictionResponse,
  RegisterPayload,
  ResultsSummaryResponse,
  UserPublic,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function requestJSON<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getResultsSummary(): Promise<ResultsSummaryResponse> {
  return requestJSON<ResultsSummaryResponse>('/results/summary');
}

export async function getModelInfo(token?: string): Promise<ModelInfo> {
  return requestJSON<ModelInfo>('/models/info', undefined, token);
}

export async function getMockPrediction(imageName?: string, parcelId?: string, token?: string): Promise<PredictionResponse> {
  return requestJSON<PredictionResponse>('/predict/mock', {
    method: 'POST',
    body: JSON.stringify({ image_name: imageName, parcel_id: parcelId }),
  }, token);
}

export async function predictImage(image: File, parcelId?: string, token?: string): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append('image', image);
  if (parcelId) {
    formData.append('parcel_id', parcelId);
  }

  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: formData,
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<PredictionResponse>;
}

export async function getHistory(userId: string, token?: string, parcelId?: string): Promise<HistoryListResponse> {
  const query = parcelId ? `?parcel_id=${encodeURIComponent(parcelId)}` : '';
  return requestJSON<HistoryListResponse>(`/history/${encodeURIComponent(userId)}${query}`, undefined, token);
}

export async function getHistoryEntry(userId: string, analysisId: string, token?: string): Promise<HistoryEntry> {
  return requestJSON<HistoryEntry>(`/history/${encodeURIComponent(userId)}/analyses/${encodeURIComponent(analysisId)}`, undefined, token);
}

export async function getCurrentUser(token: string): Promise<UserPublic> {
  return requestJSON<UserPublic>('/auth/me', undefined, token);
}

export async function loginUser(payload: LoginPayload): Promise<AuthSession> {
  return requestJSON<AuthSession>('/auth/login', { method: 'POST', body: JSON.stringify(payload) });
}

export async function registerUser(payload: RegisterPayload): Promise<AuthSession> {
  return requestJSON<AuthSession>('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
}

export async function logoutUser(token: string): Promise<void> {
  await requestJSON('/auth/logout', { method: 'POST' }, token);
}

async function downloadBlob(path: string, filename: string, token?: string): Promise<void> {
  const response = await fetch(`${API_BASE}${path}`, {
    cache: 'no-store',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
}

export async function downloadHistoryCsv(userId: string, token?: string, parcelId?: string): Promise<void> {
  const query = parcelId ? `?parcel_id=${encodeURIComponent(parcelId)}` : '';
  return downloadBlob(`/history/${encodeURIComponent(userId)}/export/csv${query}`, `soilai_history_${userId}.csv`, token);
}

export async function downloadHistoryPdf(userId: string, token?: string, parcelId?: string): Promise<void> {
  const query = parcelId ? `?parcel_id=${encodeURIComponent(parcelId)}` : '';
  return downloadBlob(`/history/${encodeURIComponent(userId)}/export/pdf${query}`, `soilai_history_${userId}.pdf`, token);
}

export async function listParcels(token: string): Promise<ParcelPublic[]> {
  return requestJSON<ParcelPublic[]>('/parcels', undefined, token);
}

export async function createParcel(payload: ParcelCreatePayload, token: string): Promise<ParcelPublic> {
  return requestJSON<ParcelPublic>('/parcels', { method: 'POST', body: JSON.stringify(payload) }, token);
}

export async function updateParcel(parcelId: string, payload: ParcelUpdatePayload, token: string): Promise<ParcelPublic> {
  return requestJSON<ParcelPublic>(`/parcels/${encodeURIComponent(parcelId)}`, { method: 'PATCH', body: JSON.stringify(payload) }, token);
}

export async function deleteParcel(parcelId: string, token: string): Promise<void> {
  await requestJSON(`/parcels/${encodeURIComponent(parcelId)}`, { method: 'DELETE' }, token);
}

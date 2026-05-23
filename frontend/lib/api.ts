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

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000';

// ── Generic fetch helpers ────────────────────────────────────────────────

const REQUEST_TIMEOUT_MS = 30_000;

async function fetchWithTimeout(
  input: RequestInfo,
  init?: RequestInit,
  timeoutMs: number = REQUEST_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  const contentType = response.headers.get('content-type') ?? '';
  const clone = response.clone();

  if (contentType.includes('application/json')) {
    try {
      const payload = (await clone.json()) as { detail?: unknown; message?: unknown } | unknown;
      if (payload && typeof payload === 'object') {
        const detail = (payload as { detail?: unknown }).detail;
        const message = (payload as { message?: unknown }).message;

        if (typeof detail === 'string' && detail.trim()) {
          return detail;
        }

        if (typeof message === 'string' && message.trim()) {
          return message;
        }

        if (Array.isArray(detail)) {
          const details = detail
            .map((item) => {
              if (item && typeof item === 'object') {
                const typedItem = item as { loc?: unknown; msg?: unknown };
                const location = Array.isArray(typedItem.loc) ? typedItem.loc.join('.') : null;
                const text = typeof typedItem.msg === 'string' ? typedItem.msg : null;
                if (location && text) {
                  return `${location}: ${text}`;
                }
                return text;
              }
              return null;
            })
            .filter((item): item is string => Boolean(item));

          if (details.length > 0) {
            return details.join(' | ');
          }
        }
      }
    } catch {
      // Fall through to plain text below.
    }
  }

  try {
    const text = await clone.text();
    if (text.trim()) {
      return text.trim();
    }
  } catch {
    // Ignore and fall through.
  }

  return `Request failed: ${response.status}`;
}

async function requestJSON<T>(
  path: string,
  init?: RequestInit,
  token?: string,
): Promise<T> {
  const response = await fetchWithTimeout(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  });

  if (response.status === 401) {
    throw new Error('unauthorized');
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    const errMsg = await readErrorMessage(response);
    console.error(`[API] ${path} → ${response.status}: ${errMsg}`);
    throw new Error(errMsg);
  }

  return (response.json() as Promise<T>).catch((e) => {
    console.error(`[API] ${path} → JSON parse error:`, e);
    throw new Error('Réponse du serveur invalide (JSON parse error)');
  });
}

// ── Public API functions ────────────────────────────────────────────────

export async function getResultsSummary(): Promise<ResultsSummaryResponse> {
  return requestJSON<ResultsSummaryResponse>('/results/summary');
}

export async function getModelInfo(token?: string): Promise<ModelInfo> {
  return requestJSON<ModelInfo>('/models/info', undefined, token);
}

export async function getMockPrediction(
  imageName?: string,
  parcelId?: string,
  token?: string,
): Promise<PredictionResponse> {
  return requestJSON<PredictionResponse>(
    '/predict/mock',
    {
      method: 'POST',
      body: JSON.stringify({ image_name: imageName, parcel_id: parcelId }),
    },
    token,
  );
}

/**
 * Upload a soil image for real NPK prediction.
 *
 * The backend runs heavy ML inference off the event loop, so we allow up to
 * 5 minutes (300 000 ms) before the client aborts.
 */
export async function predictImage(
  image: File,
  parcelId?: string,
  token?: string,
): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append('image', image);
  if (parcelId) {
    formData.append('parcel_id', parcelId);
  }

  const TIMEOUT_MS = 120_000;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      body: formData,
      cache: 'no-store',
      signal: controller.signal,
    });
  } catch (abortErr) {
    clearTimeout(timeoutId);
    if (abortErr instanceof DOMException && abortErr.name === 'AbortError') {
      console.error(
        '[predictImage] Timeout après %d secondes – le modèle est peut-être encore en cours de chargement.',
        TIMEOUT_MS / 1000,
      );
      throw new Error(
        `timeout: l'analyse a dépassé ${TIMEOUT_MS / 1000}s. Réessayez ou vérifiez que le modèle est bien chargé.`,
      );
    }
    console.error('[predictImage] Fetch error:', abortErr);
    throw abortErr;
  }
  clearTimeout(timeoutId);

  if (response.status === 401) {
    console.error('[predictImage] 401 Unauthorized – token expiré ou invalide');
    throw new Error('unauthorized');
  }

  if (!response.ok) {
    const errBody = await response.text();
    console.error('[predictImage] Error response %d: %s', response.status, errBody);

    // Try to parse a structured error from the backend
    try {
      const json = JSON.parse(errBody);
      throw new Error(json.message || json.detail || `Erreur ${response.status}`);
    } catch {
      throw new Error(errBody || `Erreur ${response.status}`);
    }
  }

  try {
    return (await response.json()) as PredictionResponse;
  } catch (e) {
    console.error('[predictImage] JSON parse error:', e);
    throw new Error('Réponse invalide du serveur');
  }
}

export async function getHistory(
  userId: string,
  token?: string,
  parcelId?: string,
): Promise<HistoryListResponse> {
  const query = parcelId ? `?parcel_id=${encodeURIComponent(parcelId)}` : '';
  return requestJSON<HistoryListResponse>(
    `/history/users/${encodeURIComponent(userId)}${query}`,
    undefined,
    token,
  );
}

export async function getHistoryEntry(
  userId: string,
  analysisId: string,
  token?: string,
): Promise<HistoryEntry> {
  void userId;
  return requestJSON<HistoryEntry>(
    `/history/${encodeURIComponent(analysisId)}`,
    undefined,
    token,
  );
}

export async function getCurrentUser(token: string): Promise<UserPublic> {
  return requestJSON<UserPublic>('/auth/me', undefined, token);
}

export async function loginUser(payload: LoginPayload): Promise<AuthSession> {
  return requestJSON<AuthSession>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function registerUser(payload: RegisterPayload): Promise<AuthSession> {
  return requestJSON<AuthSession>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function logoutUser(token: string): Promise<void> {
  await requestJSON('/auth/logout', { method: 'POST' }, token);
}

async function downloadBlob(
  path: string,
  filename: string,
  token?: string,
): Promise<void> {
  let response: Response;
  try {
    response = await fetchWithTimeout(`${API_BASE}${path}`, {
      cache: 'no-store',
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('timeout');
    }
    throw error;
  }

  if (response.status === 401) {
    throw new Error('unauthorized');
  }
  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
}

export async function downloadHistoryCsv(
  userId: string,
  token?: string,
  parcelId?: string,
): Promise<void> {
  const query = parcelId ? `?parcel_id=${encodeURIComponent(parcelId)}` : '';
  return downloadBlob(
    `/history/${encodeURIComponent(userId)}/export/csv${query}`,
    `soilai_history_${userId}.csv`,
    token,
  );
}

export async function downloadHistoryPdf(
  userId: string,
  token?: string,
  parcelId?: string,
): Promise<void> {
  const query = parcelId ? `?parcel_id=${encodeURIComponent(parcelId)}` : '';
  return downloadBlob(
    `/history/${encodeURIComponent(userId)}/export/pdf${query}`,
    `soilai_history_${userId}.pdf`,
    token,
  );
}

export async function listParcels(token: string): Promise<ParcelPublic[]> {
  return requestJSON<ParcelPublic[]>('/parcels', undefined, token);
}

export async function createParcel(
  payload: ParcelCreatePayload,
  token: string,
): Promise<ParcelPublic> {
  return requestJSON<ParcelPublic>('/parcels', {
    method: 'POST',
    body: JSON.stringify(payload),
  }, token);
}

export async function updateParcel(
  parcelId: string,
  payload: ParcelUpdatePayload,
  token: string,
): Promise<ParcelPublic> {
  return requestJSON<ParcelPublic>(
    `/parcels/${encodeURIComponent(parcelId)}`,
    { method: 'PATCH', body: JSON.stringify(payload) },
    token,
  );
}

export async function deleteParcel(parcelId: string, token: string): Promise<void> {
  await requestJSON(`/parcels/${encodeURIComponent(parcelId)}`, { method: 'DELETE' }, token);
}
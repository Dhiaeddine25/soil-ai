"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { getCurrentUser, loginUser, logoutUser, registerUser } from '@/lib/api';
import type { AuthSession, AuthState, UserPublic } from '@/lib/types';

const AUTH_TOKEN_KEY = 'soilai_token';

type AuthContextValue = AuthState & {
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: { email: string; password: string; full_name?: string | null }) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function getStoredToken() {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

function setStoredToken(token: string | null) {
  if (typeof window === 'undefined') {
    return;
  }
  if (token) {
    window.localStorage.setItem(AUTH_TOKEN_KEY, token);
  } else {
    window.localStorage.removeItem(AUTH_TOKEN_KEY);
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserPublic | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const logAuth = (message: string, detail?: unknown) => {
    console.info(`[auth] ${message}`, detail ?? '');
  };

  const mapAuthError = (err: unknown) => {
    if (err instanceof Error) {
      if (err.message === 'timeout') {
        return 'Le serveur est temporairement inaccessible.';
      }
      if (err.message === 'unauthorized') {
        return 'Session invalide. Merci de vous reconnecter.';
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Impossible de contacter le serveur.';
  };

  const applySession = useCallback((session: AuthSession) => {
    setToken(session.access_token);
    setUser(session.user);
    setStoredToken(session.access_token);
    setError(null);
    setLoading(false);
  }, []);

  const refresh = useCallback(async () => {
    const storedToken = getStoredToken();
    logAuth('refresh:start', storedToken ? 'token found' : 'no token');
    if (!storedToken) {
      setToken(null);
      setUser(null);
      setError(null);
      setLoading(false);
      return;
    }

    try {
      const current = await getCurrentUser(storedToken);
      setToken(storedToken);
      setUser(current);
      setError(null);
      logAuth('refresh:success', current.id);
    } catch (err) {
      const message = mapAuthError(err);
      logAuth('refresh:error', message);
      if (err instanceof Error && err.message === 'unauthorized') {
        setToken(null);
        setUser(null);
        setStoredToken(null);
      } else {
        setToken(null);
        setUser(null);
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const session = await loginUser({ email, password });
      applySession(session);
      logAuth('login:success', email);
    } catch (err) {
      const message = mapAuthError(err);
      logAuth('login:error', message);
      setError(message);
      setLoading(false);
      throw err;
    }
  }, [applySession]);

  const register = useCallback(async (payload: { email: string; password: string; full_name?: string | null }) => {
    setLoading(true);
    setError(null);
    try {
      const session = await registerUser(payload);
      applySession(session);
      logAuth('register:success', payload.email);
    } catch (err) {
      const message = mapAuthError(err);
      logAuth('register:error', message);
      setError(message);
      setLoading(false);
      throw err;
    }
  }, [applySession]);

  const logout = useCallback(async () => {
    setLoading(true);
    const currentToken = getStoredToken();
    if (currentToken) {
      await logoutUser(currentToken);
    }
    setToken(null);
    setUser(null);
    setStoredToken(null);
    setError(null);
    setLoading(false);
  }, []);

  const status = loading
    ? 'loading'
    : error
      ? 'error'
      : token && user
        ? 'authenticated'
        : 'unauthenticated';

  const value = useMemo<AuthContextValue>(() => ({
    user,
    loading,
    isAuthenticated: Boolean(token && user),
    status,
    error,
    token,
    login,
    register,
    logout,
    refresh,
  }), [user, loading, token, status, error, login, register, logout, refresh]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

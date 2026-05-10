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

  const applySession = useCallback((session: AuthSession) => {
    setToken(session.access_token);
    setUser(session.user);
    setStoredToken(session.access_token);
  }, []);

  const refresh = useCallback(async () => {
    const storedToken = getStoredToken();
    if (!storedToken) {
      setToken(null);
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const current = await getCurrentUser(storedToken);
      setToken(storedToken);
      setUser(current);
    } catch {
      setToken(null);
      setUser(null);
      setStoredToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = useCallback(async (email: string, password: string) => {
    const session = await loginUser({ email, password });
    applySession(session);
  }, [applySession]);

  const register = useCallback(async (payload: { email: string; password: string; full_name?: string | null }) => {
    const session = await registerUser(payload);
    applySession(session);
  }, [applySession]);

  const logout = useCallback(async () => {
    const currentToken = getStoredToken();
    if (currentToken) {
      await logoutUser(currentToken);
    }
    setToken(null);
    setUser(null);
    setStoredToken(null);
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    loading,
    isAuthenticated: Boolean(token && user),
    token,
    login,
    register,
    logout,
    refresh,
  }), [user, loading, token, login, register, logout, refresh]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

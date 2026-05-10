"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { defaultLocale, getDirection, localeStorageKey, normalizeLocale, supportedLocales, type Direction, type Locale, getMessages } from '@/lib/i18n';

type I18nContextValue = {
  locale: Locale;
  direction: Direction;
  supportedLocales: Locale[];
  messages: ReturnType<typeof getMessages>;
  setLocale: (locale: Locale) => void;
  toggleLocale: (locale: Locale) => void;
};

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

function getInitialLocale(): Locale {
  if (typeof window === 'undefined') {
    return defaultLocale;
  }

  const stored = window.localStorage.getItem(localeStorageKey);
  if (stored) {
    return normalizeLocale(stored);
  }

  const browserLocale = normalizeLocale(window.navigator.language);
  return supportedLocales.includes(browserLocale) ? browserLocale : defaultLocale;
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);

  useEffect(() => {
    const nextLocale = getInitialLocale();
    setLocaleState(nextLocale);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    window.localStorage.setItem(localeStorageKey, locale);
    document.documentElement.lang = locale;
    document.documentElement.dir = getDirection(locale);
  }, [locale]);

  const setLocale = useCallback((nextLocale: Locale) => {
    setLocaleState(nextLocale);
  }, []);

  const toggleLocale = useCallback((nextLocale: Locale) => {
    setLocaleState(nextLocale);
  }, []);

  const value = useMemo<I18nContextValue>(() => ({
    locale,
    direction: getDirection(locale),
    supportedLocales,
    messages: getMessages(locale),
    setLocale,
    toggleLocale,
  }), [locale, setLocale, toggleLocale]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
}

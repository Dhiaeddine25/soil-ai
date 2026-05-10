"use client";

import { ChevronDown, Check } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

import { useI18n } from '@/components/i18n/i18n-provider';
import { Button } from '@/components/ui/button';
import type { Locale } from '@/lib/i18n';

const labels: Record<Locale, { short: string; full: string }> = {
  fr: { short: 'FR', full: 'Français' },
  en: { short: 'EN', full: 'English' },
  ar: { short: 'AR', full: 'العربية' },
};

export function LanguageSwitcher({ compact = false }: { compact?: boolean }) {
  const { locale, setLocale, supportedLocales, messages } = useI18n();
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handlePointerDown = (event: MouseEvent) => {
      if (!wrapperRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    document.addEventListener('mousedown', handlePointerDown);
    return () => document.removeEventListener('mousedown', handlePointerDown);
  }, []);

  const currentLabel = useMemo(() => labels[locale], [locale]);

  return (
    <div ref={wrapperRef} className="relative inline-flex">
      <Button
        type="button"
        variant="ghost"
        className={compact ? 'h-10 rounded-full border border-soil-200 bg-white px-3 text-sm shadow-sm' : 'h-11 rounded-full border border-soil-200 bg-white px-4 text-sm shadow-sm'}
        onClick={() => setOpen((current) => !current)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={`${messages.shell.language}: ${currentLabel.full}`}
      >
        <span className="font-semibold tracking-wide">{currentLabel.short}</span>
        <ChevronDown className={open ? 'h-4 w-4 rotate-180 transition-transform' : 'h-4 w-4 transition-transform'} />
      </Button>

      {open ? (
        <div
          role="menu"
          className="absolute right-0 top-full z-50 mt-2 w-56 overflow-hidden rounded-[1.25rem] border border-soil-200 bg-white shadow-[0_18px_50px_rgba(68,64,60,0.18)]"
        >
          {supportedLocales.map((item) => {
            const active = item === locale;
            return (
              <button
                key={item}
                type="button"
                role="menuitemradio"
                aria-checked={active}
                onClick={() => {
                  setLocale(item);
                  setOpen(false);
                }}
                className={`flex w-full items-center justify-between px-4 py-3 text-left transition ${active ? 'bg-leaf-50 text-soil-900' : 'bg-white text-soil-700 hover:bg-stone-50'}`}
              >
                <span>
                  <span className="block text-sm font-semibold">{labels[item].full}</span>
                  <span className="block text-xs text-soil-500">{labels[item].short}</span>
                </span>
                {active ? <Check className="h-4 w-4 text-leaf-600" /> : null}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

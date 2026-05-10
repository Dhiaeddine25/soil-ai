"use client";

import dynamic from 'next/dynamic';
import { ChevronDown, ChevronUp, MapPin, Search, X } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const LocationMap = dynamic(
  () => import('./location-map').then((module) => module.LocationMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-72 items-center justify-center rounded-[1.5rem] border border-stone-200 bg-stone-50 text-sm text-stone-500">
        Carte en cours de chargement...
      </div>
    ),
  },
);

export type ParcelLocationValue = {
  address: string;
  latitude: number | null;
  longitude: number | null;
};

type GeoSuggestion = {
  address: string;
  latitude: number;
  longitude: number;
  displayLabel: string;
};

type LocationPickerProps = {
  label?: string;
  description?: string;
  value: ParcelLocationValue;
  onChange: (value: ParcelLocationValue) => void;
};

async function searchLocations(query: string): Promise<GeoSuggestion[]> {
  const response = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&addressdetails=1&limit=5&q=${encodeURIComponent(query)}`, {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Search request failed');
  }

  const results = (await response.json()) as Array<{
    display_name: string;
    lat: string;
    lon: string;
  }>;

  return results.map((item) => ({
    address: item.display_name,
    latitude: Number(item.lat),
    longitude: Number(item.lon),
    displayLabel: item.display_name,
  }));
}

async function reverseLocation(latitude: number, longitude: number): Promise<ParcelLocationValue | null> {
  const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`, {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    return null;
  }

  const result = await response.json() as { display_name?: string };
  return {
    address: result.display_name ?? 'Position sélectionnée',
    latitude,
    longitude,
  };
}

export function LocationPicker({ label = 'Localisation', description = 'Rechercher une adresse, choisir une suggestion ou cliquer sur la carte.', value, onChange }: LocationPickerProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState(value.address);
  const [suggestions, setSuggestions] = useState<GeoSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isResolving, setIsResolving] = useState(false);

  useEffect(() => {
    setQuery(value.address);
  }, [value.address]);

  useEffect(() => {
    const onPointerDown = (event: MouseEvent) => {
      if (!wrapperRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', onPointerDown);
    return () => document.removeEventListener('mousedown', onPointerDown);
  }, []);

  useEffect(() => {
    const term = query.trim();

    if (term.length < 3) {
      setSuggestions([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    const timeout = window.setTimeout(async () => {
      try {
        const results = await searchLocations(term);
        setSuggestions(results);
      } catch {
        setSuggestions([]);
      } finally {
        setIsSearching(false);
      }
    }, 280);

    return () => window.clearTimeout(timeout);
  }, [query]);

  const selectedSummary = useMemo(() => {
    if (!value.address) {
      return null;
    }

    const coordinates = value.latitude != null && value.longitude != null ? `${value.latitude.toFixed(5)}, ${value.longitude.toFixed(5)}` : 'Coordonnées non définies';
    return `${value.address} · ${coordinates}`;
  }, [value.address, value.latitude, value.longitude]);

  const chooseSuggestion = (suggestion: GeoSuggestion) => {
    setQuery(suggestion.displayLabel);
    setSuggestions([]);
    setIsOpen(false);
    onChange({
      address: suggestion.address,
      latitude: suggestion.latitude,
      longitude: suggestion.longitude,
    });
  };

  const handleMapSelect = async (latitude: number, longitude: number) => {
    setIsResolving(true);
    try {
      const resolved = await reverseLocation(latitude, longitude);
      const nextValue = resolved ?? {
        address: `Position sélectionnée (${latitude.toFixed(5)}, ${longitude.toFixed(5)})`,
        latitude,
        longitude,
      };

      setQuery(nextValue.address);
      onChange(nextValue);
      setIsOpen(false);
    } finally {
      setIsResolving(false);
    }
  };

  const clearLocation = () => {
    setQuery('');
    setSuggestions([]);
    onChange({ address: '', latitude: null, longitude: null });
  };

  return (
    <div ref={wrapperRef} className="space-y-3">
      <div className="space-y-2 text-sm font-medium text-soil-700">
        <span>{label}</span>
        <div className="relative">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-soil-400" />
          <input
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && suggestions[0]) {
                event.preventDefault();
                chooseSuggestion(suggestions[0]);
              }
            }}
            className="w-full rounded-2xl border border-soil-200 bg-white px-11 py-3 outline-none transition focus:border-leaf-500"
            placeholder="Adresse, village, ville, point GPS..."
            autoComplete="off"
          />
          {value.address ? (
            <button
              type="button"
              onClick={clearLocation}
              className="absolute right-3 top-1/2 flex -translate-y-1/2 items-center justify-center rounded-full p-1 text-soil-400 transition hover:bg-stone-100 hover:text-soil-700"
              aria-label="Effacer la localisation"
            >
              <X className="h-4 w-4" />
            </button>
          ) : null}
        </div>
        <div className="text-xs leading-5 text-soil-500">{description}</div>
      </div>

      <div className="relative">
        {isOpen && (suggestions.length > 0 || isSearching) ? (
          <div className="absolute left-0 right-0 top-0 z-30 mt-2 overflow-hidden rounded-[1.35rem] border border-stone-200 bg-white shadow-soft">
            {isSearching ? (
              <div className="px-4 py-3 text-sm text-soil-500">Recherche de lieux...</div>
            ) : null}
            {suggestions.map((suggestion) => (
              <button
                key={`${suggestion.latitude}-${suggestion.longitude}-${suggestion.address}`}
                type="button"
                onClick={() => chooseSuggestion(suggestion)}
                className="flex w-full items-start gap-3 border-t border-stone-100 px-4 py-3 text-left transition hover:bg-stone-50"
              >
                <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-leaf-600" />
                <div>
                  <div className="text-sm font-medium text-stone-900">{suggestion.displayLabel}</div>
                  <div className="text-xs text-stone-500">{suggestion.latitude.toFixed(5)}, {suggestion.longitude.toFixed(5)}</div>
                </div>
              </button>
            ))}
            {!isSearching && suggestions.length === 0 ? (
              <div className="border-t border-stone-100 px-4 py-3 text-sm text-stone-500">Aucune suggestion trouvée.</div>
            ) : null}
          </div>
        ) : null}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="overflow-hidden rounded-[1.5rem] border border-stone-200 bg-stone-50 shadow-sm">
          {isResolving ? (
            <div className="flex h-72 items-center justify-center text-sm text-stone-500">Sélection du point et résolution de l’adresse...</div>
          ) : (
            <LocationMap latitude={value.latitude} longitude={value.longitude} onSelect={(latitude, longitude) => void handleMapSelect(latitude, longitude)} />
          )}
        </div>

        <div className="space-y-3 rounded-[1.5rem] border border-stone-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Position enregistrée</div>
              <div className="mt-1 text-sm font-semibold text-stone-900">Adresse, latitude, longitude</div>
            </div>
            <div className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-xs font-medium text-stone-600">
              {value.latitude != null && value.longitude != null ? 'Sélectionnée' : 'En attente'}
            </div>
          </div>

          {selectedSummary ? (
            <div className="rounded-2xl border border-leaf-100 bg-leaf-50 px-4 py-3 text-sm leading-6 text-stone-800">
              {selectedSummary}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-stone-200 bg-stone-50 px-4 py-3 text-sm leading-6 text-stone-500">
              Choisis une adresse dans les suggestions ou clique sur la carte pour placer la parcelle.
            </div>
          )}

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-2xl border border-stone-200 bg-stone-50 px-4 py-3">
              <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Latitude</div>
              <div className={cn('mt-2 font-semibold', value.latitude == null ? 'text-stone-400' : 'text-stone-900')}>
                {value.latitude != null ? value.latitude.toFixed(6) : '—'}
              </div>
            </div>
            <div className="rounded-2xl border border-stone-200 bg-stone-50 px-4 py-3">
              <div className="text-xs uppercase tracking-[0.18em] text-stone-500">Longitude</div>
              <div className={cn('mt-2 font-semibold', value.longitude == null ? 'text-stone-400' : 'text-stone-900')}>
                {value.longitude != null ? value.longitude.toFixed(6) : '—'}
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={clearLocation}
            className="inline-flex items-center justify-center rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-stone-700 transition hover:bg-stone-50"
          >
            Réinitialiser la localisation
          </button>
        </div>
      </div>
    </div>
  );
}
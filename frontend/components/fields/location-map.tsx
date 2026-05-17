"use client";

import { useEffect, useRef } from 'react';

import L from 'leaflet';
import type { LeafletMouseEvent, Map as LeafletMap, CircleMarker as LeafletCircleMarker } from 'leaflet';

const defaultCenter: [number, number] = [31.7917, -7.0926];

// We implement the Leaflet map manually to ensure a single definitive
// initialization and a clean teardown with `map.remove()` on unmount.
// This avoids the common "Map container is already initialized" error
// that appears in dev (StrictMode / HMR) when the container is reused.

export function LocationMap({
  latitude,
  longitude,
  onSelect,
}: {
  latitude: number | null;
  longitude: number | null;
  onSelect: (latitude: number, longitude: number) => void;
}) {
  const hasLocation = latitude != null && longitude != null;
  const center: [number, number] = hasLocation ? [latitude, longitude] : defaultCenter;

  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const markerRef = useRef<LeafletCircleMarker | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    // If a previous map exists, remove it before creating a new one.
    if (mapRef.current) {
      try {
        mapRef.current.remove();
      } catch {}
      mapRef.current = null;
    }

    const map = L.map(el, { center, zoom: hasLocation ? 15 : 5, scrollWheelZoom: true });
    mapRef.current = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    if (hasLocation) {
      markerRef.current = L.circleMarker(center, {
        radius: 10,
        color: '#365314',
        fillColor: '#84cc16',
        fillOpacity: 0.7,
      }).addTo(map);
    }

    const handleClick = (e: LeafletMouseEvent) => onSelect(e.latlng.lat, e.latlng.lng);
    map.on('click', handleClick);

    return () => {
      map.off('click', handleClick);
      try {
        map.remove();
      } catch {}
      mapRef.current = null;
      markerRef.current = null;
    };
  // Recreate map only when the container element reference changes; center/marker updates
  // are handled in a separate effect below to avoid remount churn.
  }, [containerRef.current]);

  // Update marker and view when latitude/longitude change without recreating the map.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (hasLocation) {
      map.setView(center, 15, { animate: true });
      if (markerRef.current) {
        markerRef.current.setLatLng(center);
      } else {
        markerRef.current = L.circleMarker(center, {
          radius: 10,
          color: '#365314',
          fillColor: '#84cc16',
          fillOpacity: 0.7,
        }).addTo(map);
      }
    } else {
      map.setView(defaultCenter, 5, { animate: true });
      if (markerRef.current) {
        markerRef.current.remove();
        markerRef.current = null;
      }
    }
  }, [latitude, longitude]);

  return <div ref={containerRef} className="h-72 w-full rounded-[1.5rem]" />;
}

// Ensure we clean up the Leaflet instance if this module is hot-reloaded or
// React remounts rapidly in StrictMode. The `whenCreated` handler above uses
// the local `mapRef` and the cleanup is handled per-instance in React lifecycles.
"use client";

import { useEffect } from 'react';

import type { LeafletMouseEvent } from 'leaflet';
import { CircleMarker, MapContainer, TileLayer, useMap, useMapEvents } from 'react-leaflet';

const defaultCenter: [number, number] = [31.7917, -7.0926];

function MapEvents({ onSelect }: { onSelect: (latitude: number, longitude: number) => void }) {
  useMapEvents({
    click(event: LeafletMouseEvent) {
      onSelect(event.latlng.lat, event.latlng.lng);
    },
  });

  return null;
}

function MapUpdater({ latitude, longitude }: { latitude: number | null; longitude: number | null }) {
  const map = useMap();

  useEffect(() => {
    if (latitude == null || longitude == null) {
      return;
    }

    map.setView([latitude, longitude], 15, { animate: true });
  }, [latitude, longitude, map]);

  return null;
}

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

  return (
    <MapContainer center={center} zoom={hasLocation ? 15 : 5} scrollWheelZoom className="h-72 w-full rounded-[1.5rem]">
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {hasLocation ? (
        <CircleMarker
          center={center}
          radius={10}
          pathOptions={{ color: '#365314', fillColor: '#84cc16', fillOpacity: 0.7 }}
        />
      ) : null}
      <MapEvents onSelect={onSelect} />
      <MapUpdater latitude={latitude} longitude={longitude} />
    </MapContainer>
  );
}
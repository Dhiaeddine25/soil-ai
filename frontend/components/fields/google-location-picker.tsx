"use client";

import { useEffect, useMemo, useRef, useState } from 'react';

import { LocationPicker, ParcelLocationValue } from '@/components/fields/location-picker';

const googleApiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? '';

function loadGoogleMaps(apiKey: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') {
      reject(new Error('window not available'));
      return;
    }

    if ((window as any).google?.maps) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('google maps failed'));
    document.head.appendChild(script);
  });
}

type GoogleLocationPickerProps = {
  value: ParcelLocationValue;
  onChange: (value: ParcelLocationValue) => void;
  label?: string;
  description?: string;
};

export function GoogleLocationPicker({ value, onChange, label, description }: GoogleLocationPickerProps) {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const markerInstance = useRef<any>(null);

  useEffect(() => {
    if (!googleApiKey) {
      return;
    }

    loadGoogleMaps(googleApiKey)
      .then(() => setReady(true))
      .catch(() => setError('Google Maps indisponible.')); 
  }, []);

  useEffect(() => {
    if (!ready || !inputRef.current) {
      return;
    }

    const autocomplete = new (window as any).google.maps.places.Autocomplete(inputRef.current, {
      fields: ['formatted_address', 'geometry'],
      types: ['geocode'],
    });

    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      const location = place.geometry?.location;
      if (!location) {
        return;
      }

      onChange({
        address: place.formatted_address ?? value.address,
        latitude: location.lat(),
        longitude: location.lng(),
      });
    });

    return () => {
      (window as any).google.maps.event.clearInstanceListeners(autocomplete);
    };
  }, [ready, onChange, value.address]);

  useEffect(() => {
    if (!ready || !mapRef.current) {
      return;
    }

    if (!mapInstance.current) {
      mapInstance.current = new (window as any).google.maps.Map(mapRef.current, {
        center: { lat: value.latitude ?? 31.7917, lng: value.longitude ?? -7.0926 },
        zoom: value.latitude && value.longitude ? 14 : 5,
        mapTypeControl: false,
        streetViewControl: false,
      });

      mapInstance.current.addListener('click', (event: any) => {
        if (!event.latLng) {
          return;
        }
        const lat = event.latLng.lat();
        const lng = event.latLng.lng();
        onChange({ address: value.address || 'Position sélectionnée', latitude: lat, longitude: lng });
      });
    }

    if (value.latitude != null && value.longitude != null) {
      const position = { lat: value.latitude, lng: value.longitude };
      if (!markerInstance.current) {
        markerInstance.current = new (window as any).google.maps.Marker({
          position,
          map: mapInstance.current,
          draggable: true,
        });
        markerInstance.current.addListener('dragend', (event: any) => {
          if (!event.latLng) {
            return;
          }
          onChange({
            address: value.address || 'Position sélectionnée',
            latitude: event.latLng.lat(),
            longitude: event.latLng.lng(),
          });
        });
      } else {
        markerInstance.current.setPosition(position);
      }
      mapInstance.current?.setCenter(position);
      mapInstance.current?.setZoom(14);
    }
  }, [ready, value.latitude, value.longitude, value.address, onChange]);

  const helper = useMemo(() => {
    if (!googleApiKey) {
      return 'Ajoute ta cle Google Maps pour activer la recherche intelligente.';
    }
    if (error) {
      return 'Impossible de charger Google Maps. Verifie ta cle API.';
    }
    return description;
  }, [error, description]);

  if (!googleApiKey) {
    return <LocationPicker value={value} onChange={onChange} label={label} description={helper} />;
  }

  return (
    <div className="space-y-3">
      <label className="block space-y-2 text-sm font-medium text-soil-700">
        <span>{label ?? 'Localisation'}</span>
        <input
          ref={inputRef}
          defaultValue={value.address}
          className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500"
          placeholder="Adresse, village, ville..."
        />
        <div className="text-xs text-soil-500">{helper}</div>
      </label>
      <div className="h-72 overflow-hidden rounded-[1.5rem] border border-soil-200 bg-soil-50" ref={mapRef} />
    </div>
  );
}

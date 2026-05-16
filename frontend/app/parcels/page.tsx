"use client";

import { useEffect, useMemo, useState } from 'react';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { GoogleLocationPicker } from '@/components/fields/google-location-picker';
import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { createParcel, deleteParcel, listParcels, updateParcel } from '@/lib/api';
import type { ParcelPublic } from '@/lib/types';

type ParcelLocationValue = {
  address: string;
  latitude: number | null;
  longitude: number | null;
};

function ParcelsContent({ focusParcelId }: { focusParcelId?: string }) {
  const { token, user } = useAuth();
  const [parcels, setParcels] = useState<ParcelPublic[]>([]);
  const [name, setName] = useState('');
  const [region, setRegion] = useState('');
  const [areaHa, setAreaHa] = useState('');
  const [crop, setCrop] = useState('');
  const [notes, setNotes] = useState('');
  const [location, setLocation] = useState<ParcelLocationValue>({ address: '', latitude: null, longitude: null });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const describeError = (fallback: string, value: unknown) => {
    if (value instanceof Error) {
      if (value.message === 'unauthorized') {
        return 'Session expirée. Reconnectez-vous.';
      }
      if (value.message === 'timeout') {
        return 'Le serveur ne répond pas. Réessayez.';
      }
      return value.message || fallback;
    }

    return fallback;
  };

  const focusedParcel = useMemo(() => parcels.find((parcel) => parcel.id === focusParcelId), [parcels, focusParcelId]);

  useEffect(() => {
    const load = async () => {
      if (!token) {
        return;
      }

      try {
        setLoading(true);
        const items = await listParcels(token);
        setParcels(items);
      } catch (loadError) {
        setError(describeError('Impossible de charger les parcelles.', loadError));
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [token]);

  const resetForm = () => {
    setName('');
    setRegion('');
    setAreaHa('');
    setCrop('');
    setNotes('');
    setLocation({ address: '', latitude: null, longitude: null });
    setEditingId(null);
  };

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || !name.trim()) {
      return;
    }

    setSaving(true);
    setError(null);
    try {
      const address = location.address.trim();
      const normalizedArea = areaHa.trim().replace(',', '.');
      const areaValue = normalizedArea ? Number(normalizedArea) : null;
      if (normalizedArea && Number.isNaN(areaValue)) {
        setError('Surface estimee invalide.');
        return;
      }
      if (editingId) {
        const updated = await updateParcel(editingId, {
          name: name.trim(),
          location: address || null,
          region: region.trim() || null,
          area_ha: areaValue,
          crop: crop.trim() || null,
          notes: notes.trim() || null,
          latitude: address ? location.latitude : null,
          longitude: address ? location.longitude : null,
        }, token);
        setParcels((current) => current.map((parcel) => (parcel.id === editingId ? updated : parcel)));
      } else {
        const created = await createParcel({
          name: name.trim(),
          location: address || null,
          region: region.trim() || null,
          area_ha: areaValue,
          crop: crop.trim() || null,
          notes: notes.trim() || null,
          latitude: address ? location.latitude : null,
          longitude: address ? location.longitude : null,
        }, token);
        setParcels((current) => [created, ...current]);
      }
      resetForm();
    } catch (saveError) {
      setError(describeError('Enregistrement impossible.', saveError));
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (parcel: ParcelPublic) => {
    setEditingId(parcel.id);
    setName(parcel.name);
    setRegion(parcel.region ?? '');
    setAreaHa(parcel.area_ha != null ? String(parcel.area_ha) : '');
    setCrop(parcel.crop ?? '');
    setNotes(parcel.notes ?? '');
    setLocation({
      address: parcel.location ?? '',
      latitude: parcel.latitude ?? null,
      longitude: parcel.longitude ?? null,
    });
  };

  const handleDelete = async (parcelId: string) => {
    if (!token) {
      return;
    }

    setSaving(true);
    setError(null);
    try {
      await deleteParcel(parcelId, token);
      setParcels((current) => current.filter((parcel) => parcel.id !== parcelId));
      if (editingId === parcelId) {
        resetForm();
      }
    } catch (deleteError) {
      setError(describeError('Suppression impossible.', deleteError));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <Card className="space-y-3">
          <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Parcelles</div>
          <h1 className="text-3xl font-semibold text-soil-900">Votre base de parcelles terrain</h1>
          <div className="text-sm text-soil-600">Compte: {user?.full_name ?? user?.email}</div>
          {focusedParcel ? <div className="rounded-2xl border border-leaf-200 bg-leaf-50 px-4 py-3 text-sm text-leaf-900">Parcelle liée à l’analyse: {focusedParcel.name}</div> : null}
        </Card>

        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <Card>
            <h2 className="text-xl font-semibold text-soil-900">{editingId ? 'Modifier' : 'Ajouter'}</h2>
            <form className="mt-5 space-y-4" onSubmit={onSubmit}>
              <label className="block space-y-2 text-sm font-medium text-soil-700">
                <span>Nom</span>
                <input value={name} onChange={(event) => setName(event.target.value)} className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="Ex: Parcelle A12" />
              </label>
              <label className="block space-y-2 text-sm font-medium text-soil-700">
                <span>Region</span>
                <input value={region} onChange={(event) => setRegion(event.target.value)} className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="Ex: Souss-Massa" />
              </label>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block space-y-2 text-sm font-medium text-soil-700">
                  <span>Surface estimee (ha)</span>
                  <input value={areaHa} onChange={(event) => setAreaHa(event.target.value.replace(/[^0-9.,]/g, ''))} className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="Ex: 2.4" />
                </label>
                <label className="block space-y-2 text-sm font-medium text-soil-700">
                  <span>Culture principale</span>
                  <input value={crop} onChange={(event) => setCrop(event.target.value)} className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="Ex: Blé dur" />
                </label>
              </div>
              <GoogleLocationPicker
                value={location}
                onChange={setLocation}
                label="Localisation"
                description="Recherche une adresse ou choisis un point sur la carte."
              />
              <label className="block space-y-2 text-sm font-medium text-soil-700">
                <span>Notes terrain</span>
                <textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={4} className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="Etat de surface, irrigation, observations..." />
              </label>
              <div className="flex flex-wrap gap-3">
                <Button type="submit" disabled={saving}>{editingId ? 'Mettre à jour' : 'Créer'}</Button>
                <Button type="button" variant="ghost" onClick={resetForm}>Réinitialiser</Button>
              </div>
              {error ? <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{error}</div> : null}
            </form>
          </Card>

          <Card>
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-semibold text-soil-900">Vos parcelles</h2>
              <div className="text-sm text-soil-500">{parcels.length} parcelle(s)</div>
            </div>

            {loading ? (
              <div className="mt-6 text-sm text-soil-500">Chargement...</div>
            ) : parcels.length === 0 ? (
              <div className="mt-6 rounded-2xl border border-dashed border-soil-200 bg-soil-50 p-6 text-sm text-soil-600">Aucune parcelle enregistrée pour le moment.</div>
            ) : (
              <div className="mt-6 space-y-3">
                {parcels.map((parcel) => (
                  <div key={parcel.id} className={`rounded-2xl border p-4 ${parcel.id === focusParcelId ? 'border-leaf-300 bg-leaf-50' : 'border-soil-200 bg-white'}`}>
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="font-semibold text-soil-900">{parcel.name}</div>
                        <div className="text-sm text-soil-500">{parcel.location ?? 'Localisation non renseignée'}</div>
                        <div className="mt-2 flex flex-wrap gap-2 text-xs text-soil-500">
                          {parcel.region ? <span className="rounded-full bg-soil-100 px-2 py-1">{parcel.region}</span> : null}
                          {parcel.crop ? <span className="rounded-full bg-soil-100 px-2 py-1">{parcel.crop}</span> : null}
                          {parcel.area_ha != null ? <span className="rounded-full bg-soil-100 px-2 py-1">{parcel.area_ha} ha</span> : null}
                        </div>
                        {parcel.latitude != null && parcel.longitude != null ? (
                          <div className="mt-1 text-xs text-soil-400">
                            {parcel.latitude.toFixed(5)}, {parcel.longitude.toFixed(5)}
                          </div>
                        ) : null}
                      </div>
                      <div className="flex gap-2">
                        <Button variant="ghost" className="px-3 py-2" onClick={() => startEdit(parcel)}>Modifier</Button>
                        <Button variant="ghost" className="px-3 py-2" onClick={() => void handleDelete(parcel.id)}>Supprimer</Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function ParcelsPage({ searchParams }: { searchParams?: { focus?: string } }) {
  return (
    <ProtectedRoute>
      <ParcelsContent focusParcelId={searchParams?.focus} />
    </ProtectedRoute>
  );
}
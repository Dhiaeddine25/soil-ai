"use client";

import { useEffect, useMemo, useState } from 'react';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { LocationPicker } from '@/components/fields/location-picker';
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
  const [location, setLocation] = useState<ParcelLocationValue>({ address: '', latitude: null, longitude: null });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      } catch {
        setError('Impossible de charger les parcelles.');
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [token]);

  const resetForm = () => {
    setName('');
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
      if (editingId) {
        const updated = await updateParcel(editingId, {
          name: name.trim(),
          location: address || null,
          latitude: address ? location.latitude : null,
          longitude: address ? location.longitude : null,
        }, token);
        setParcels((current) => current.map((parcel) => (parcel.id === editingId ? updated : parcel)));
      } else {
        const created = await createParcel({
          name: name.trim(),
          location: address || null,
          latitude: address ? location.latitude : null,
          longitude: address ? location.longitude : null,
        }, token);
        setParcels((current) => [created, ...current]);
      }
      resetForm();
    } catch {
      setError('Enregistrement impossible.');
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (parcel: ParcelPublic) => {
    setEditingId(parcel.id);
    setName(parcel.name);
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
    } catch {
      setError('Suppression impossible.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <Card className="space-y-3">
          <div className="text-sm uppercase tracking-[0.18em] text-soil-500">Parcelles</div>
          <h1 className="text-3xl font-semibold text-soil-900">Créer, modifier et supprimer.</h1>
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
              <LocationPicker
                value={location}
                onChange={setLocation}
                label="Localisation"
                description="Recherche une adresse, choisis une suggestion ou clique sur la carte pour enregistrer l’adresse et les coordonnées."
              />
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
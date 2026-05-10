"use client";

import { useRouter } from 'next/navigation';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';

function ProfileContent() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { messages } = useI18n();

  return (
    <div className="px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <Card className="space-y-4">
          <div className="text-sm uppercase tracking-[0.18em] text-soil-500">{messages.profile.title}</div>
          <h1 className="text-3xl font-semibold text-soil-900">{messages.profile.subtitle}</h1>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4">
              <div className="text-sm text-soil-500">Nom</div>
              <div className="mt-1 text-lg font-semibold text-soil-900">{user?.full_name ?? 'Non renseigné'}</div>
            </div>
            <div className="rounded-2xl border border-soil-200 bg-stone-50 p-4">
              <div className="text-sm text-soil-500">Email</div>
              <div className="mt-1 text-lg font-semibold text-soil-900">{user?.email}</div>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => router.push('/upload')}>{messages.profile.newAnalysis}</Button>
            <Button variant="ghost" onClick={async () => { await logout(); router.replace('/'); }}>{messages.profile.logout}</Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
}
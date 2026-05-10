"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { Card } from '@/components/ui/card';
import { useAuth } from './auth-provider';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return (
      <div className="px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-xl">
          <Card>
            <div className="text-lg font-semibold text-soil-900">Chargement de la session...</div>
          </Card>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}

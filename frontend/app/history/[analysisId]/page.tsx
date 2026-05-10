"use client";

import { useParams } from 'next/navigation';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { HistoryDetailView } from '@/components/sections/history-detail-view';

export default function HistoryDetailPage() {
  const params = useParams<{ analysisId: string }>();

  return (
    <ProtectedRoute>
      <HistoryDetailView analysisId={params.analysisId} />
    </ProtectedRoute>
  );
}
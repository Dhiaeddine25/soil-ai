"use client";

import { ProtectedRoute } from '@/components/auth/protected-route';
import { HistoryCenter } from '@/components/sections/history-center';

export default function HistoryPage() {
  return (
    <ProtectedRoute>
      <HistoryCenter />
    </ProtectedRoute>
  );
}
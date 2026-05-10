"use client";

import { ProtectedRoute } from '@/components/auth/protected-route';
import { DashboardView } from '@/components/sections/dashboard-view';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardView />
    </ProtectedRoute>
  );
}
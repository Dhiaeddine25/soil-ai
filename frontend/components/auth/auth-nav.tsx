"use client";

import Link from 'next/link';

import { Button } from '@/components/ui/button';
import { useAuth } from './auth-provider';
import { useI18n } from '@/components/i18n/i18n-provider';

export function AuthNav() {
  const { user, isAuthenticated, logout } = useAuth();
  const { messages } = useI18n();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="hidden items-center gap-3 lg:flex">
      <Link href="/profile" className="rounded-full border border-soil-200 bg-white px-4 py-2 text-sm font-medium text-soil-700 hover:text-soil-900">
        {user?.full_name ?? user?.email}
      </Link>
      <Button variant="ghost" className="px-4 py-2" onClick={() => void logout()}>
        {messages.shell.logout}
      </Button>
    </div>
  );
}
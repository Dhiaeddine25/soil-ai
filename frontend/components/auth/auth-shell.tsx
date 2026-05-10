"use client";

import Link from 'next/link';

import { Card } from '@/components/ui/card';
import { useI18n } from '@/components/i18n/i18n-provider';

export function AuthShell({ children, variant = 'login' }: { children: React.ReactNode; variant?: 'login' | 'register' }) {
  const { messages } = useI18n();
  const title = variant === 'register' ? messages.auth.registerTitle : messages.auth.loginTitle;
  const subtitle = variant === 'register' ? messages.auth.registerSubtitle : messages.auth.loginSubtitle;

  return (
    <div className="px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="space-y-5">
          <div className="inline-flex rounded-full border border-leaf-200 bg-leaf-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-leaf-700">
            {messages.shell.appTagline}
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-soil-900 sm:text-4xl">{title}</h1>
          <p className="max-w-xl text-base leading-7 text-soil-600">{subtitle}</p>
          <div className="text-sm text-soil-600">
            <Link href="/" className="font-semibold text-leaf-700">{messages.auth.backHome}</Link>
          </div>
        </div>

        <Card className="p-6">{children}</Card>
      </div>
    </div>
  );
}
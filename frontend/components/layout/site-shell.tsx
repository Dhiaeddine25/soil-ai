"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Leaf, Sprout } from 'lucide-react';

import { AuthNav } from '@/components/auth/auth-nav';
import { useAuth } from '@/components/auth/auth-provider';
import { LanguageSwitcher } from '@/components/layout/language-switcher';
import { Button } from '@/components/ui/button';
import { useI18n } from '@/components/i18n/i18n-provider';

const privateNav = [
  { href: '/dashboard', key: 'dashboard' },
  { href: '/parcels', key: 'parcels' },
  { href: '/upload', key: 'analysis' },
  { href: '/history', key: 'history' },
  { href: '/profile', key: 'account' },
] as const;

export function SiteShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { messages } = useI18n();
  const { isAuthenticated } = useAuth();
  const isAuthPage = pathname === '/login' || pathname === '/register';
  const isPrivatePage = pathname?.startsWith('/dashboard') || pathname?.startsWith('/parcels') || pathname?.startsWith('/upload') || pathname?.startsWith('/history') || pathname?.startsWith('/profile');

  if (isAuthPage) {
    return (
      <div className="min-h-screen bg-stone-50 text-soil-900">
        <header className="border-b border-soil-200 bg-white/90 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <Link href="/" className="flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-soil-900 text-white shadow-soft">
                <Sprout className="h-5 w-5" />
              </span>
              <div>
                <div className="text-base font-semibold tracking-tight">{messages.shell.appName}</div>
                <div className="text-xs text-soil-500">{messages.shell.appTagline}</div>
              </div>
            </Link>
            <div className="flex items-center gap-3">
              <LanguageSwitcher compact />
              <Link href="/">
                <Button variant="ghost" className="px-4 py-2">
                  {messages.auth.backHome}
                </Button>
              </Link>
            </div>
          </div>
        </header>
        <main>{children}</main>
      </div>
    );
  }

  if (!isPrivatePage) {
    return (
      <div className="min-h-screen bg-stone-50 text-soil-900">
        <header className="border-b border-soil-200 bg-white/90 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
            <Link href="/" className="flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-soil-900 text-white shadow-soft">
                <Sprout className="h-5 w-5" />
              </span>
              <div>
                <div className="text-base font-semibold tracking-tight">{messages.shell.appName}</div>
                <div className="text-xs text-soil-500">{messages.shell.appTagline}</div>
              </div>
            </Link>
            <div className="flex items-center gap-3">
              <LanguageSwitcher compact />
              {isAuthenticated ? (
                <Link href="/dashboard">
                  <Button className="px-4 py-2">{messages.shell.openApp}</Button>
                </Link>
              ) : (
                <Link href="/login">
                  <Button className="px-4 py-2">{messages.shell.login}</Button>
                </Link>
              )}
            </div>
          </div>
        </header>
        <main>{children}</main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50 text-soil-900">
      <header className="sticky top-0 z-40 border-b border-soil-200 bg-white/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between gap-4">
            <Link href="/dashboard" className="flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-soil-900 text-white shadow-soft">
                <Sprout className="h-5 w-5" />
              </span>
              <div>
                <div className="text-base font-semibold tracking-tight">{messages.shell.appName}</div>
                <div className="text-xs text-soil-500">{messages.shell.appTagline}</div>
              </div>
            </Link>

            <div className="flex items-center gap-2">
              <LanguageSwitcher compact />
              <Link href="/upload">
                <Button className="hidden px-4 py-2 sm:inline-flex">
                  <Leaf className="h-4 w-4" />
                  {messages.shell.newAnalysis}
                </Button>
              </Link>
              <AuthNav />
            </div>
          </div>

          <nav className="-mx-1 flex gap-2 overflow-x-auto pb-1 text-sm">
            {privateNav.map((item) => {
              const active = pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`whitespace-nowrap rounded-full border px-4 py-2 transition ${active ? 'border-soil-900 bg-soil-900 text-white' : 'border-soil-200 bg-white text-soil-600 hover:border-soil-300 hover:text-soil-900'}`}
                >
                  {messages.shell[item.key]}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
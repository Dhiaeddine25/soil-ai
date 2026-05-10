"use client";

import Link from 'next/link';
import { ArrowRight, CheckCircle2, Layers3 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { useI18n } from '@/components/i18n/i18n-provider';

export default function HomePage() {
  const { messages } = useI18n();

  return (
    <main className="bg-stone-50 text-soil-900">
      <section className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-7xl flex-col justify-center px-4 py-16 sm:px-6 lg:px-8">
        <div className="max-w-3xl space-y-6">
          <div className="inline-flex rounded-full border border-leaf-200 bg-leaf-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-leaf-700">
            {messages.landing.eyebrow}
          </div>
          <h1 className="text-4xl font-semibold tracking-tight text-soil-900 sm:text-5xl lg:text-6xl">
            {messages.landing.title}
          </h1>
          <p className="max-w-2xl text-base leading-8 text-soil-600 sm:text-lg">
            {messages.landing.subtitle}
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/dashboard">
              <Button className="px-5 py-3">
                {messages.landing.primary}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="ghost" className="px-5 py-3">
                {messages.landing.secondary}
              </Button>
            </Link>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-sm text-soil-500">
            <div className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 shadow-sm">
              <CheckCircle2 className="h-4 w-4 text-leaf-600" />
              {messages.landing.note}
            </div>
            <div className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 shadow-sm">
              <Layers3 className="h-4 w-4 text-soil-600" />
              {messages.landing.stepsTitle}
            </div>
          </div>
        </div>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {messages.landing.steps.map((step, index) => (
            <div key={step} className="rounded-3xl border border-soil-200 bg-white p-5 shadow-sm">
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-soil-400">0{index + 1}</div>
              <div className="mt-3 text-lg font-semibold text-soil-900">{step}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
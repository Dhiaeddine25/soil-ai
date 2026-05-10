"use client";

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import { useAuth } from './auth-provider';

export function LoginForm() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    startTransition(async () => {
      try {
        await login(email, password);
        router.replace('/profile');
      } catch {
        setError('Connexion impossible. Vérifie ton email et ton mot de passe.');
      }
    });
  };

  return (
    <form className="space-y-4" onSubmit={submit}>
      <label className="block space-y-2 text-sm font-medium text-soil-700">
        <span>Email</span>
        <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="you@example.com" />
      </label>
      <label className="block space-y-2 text-sm font-medium text-soil-700">
        <span>Mot de passe</span>
        <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="********" />
      </label>
      {error ? <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{error}</div> : null}
      <Button type="submit" disabled={isPending} className="w-full">
        Se connecter
      </Button>
    </form>
  );
}

export function RegisterForm() {
  const router = useRouter();
  const { register } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    startTransition(async () => {
      try {
        await register({ email, password, full_name: fullName || null });
        router.replace('/profile');
      } catch {
        setError('Inscription impossible. Vérifie les informations et la longueur du mot de passe.');
      }
    });
  };

  return (
    <form className="space-y-4" onSubmit={submit}>
      <label className="block space-y-2 text-sm font-medium text-soil-700">
        <span>Nom complet</span>
        <input value={fullName} onChange={(event) => setFullName(event.target.value)} className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="Nom et prénom" />
      </label>
      <label className="block space-y-2 text-sm font-medium text-soil-700">
        <span>Email</span>
        <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="you@example.com" />
      </label>
      <label className="block space-y-2 text-sm font-medium text-soil-700">
        <span>Mot de passe</span>
        <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" className="w-full rounded-2xl border border-soil-200 bg-white px-4 py-3 outline-none transition focus:border-leaf-500" placeholder="Au moins 8 caractères" />
      </label>
      {error ? <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{error}</div> : null}
      <Button type="submit" disabled={isPending} className="w-full">
        Créer le compte
      </Button>
    </form>
  );
}

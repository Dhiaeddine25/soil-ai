import { cn } from '@/lib/utils';

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('rounded-3xl border border-white/60 bg-white/75 p-6 shadow-soft backdrop-blur-sm', className)} {...props} />;
}

import { cn } from '@/lib/utils';

export function AgricultureCard({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'rounded-3xl border border-soil-200 bg-white/90 p-6 shadow-soft backdrop-blur',
        className,
      )}
      {...props}
    />
  );
}

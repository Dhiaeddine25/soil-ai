import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost';
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = 'primary', ...props },
  ref,
) {
  const variants = {
    primary: 'bg-soil-900 text-white hover:bg-soil-800 shadow-soft',
    secondary: 'bg-leaf-600 text-white hover:bg-leaf-500 shadow-soft',
    ghost: 'bg-white/70 text-soil-900 border border-soil-200 hover:bg-white',
  };

  return (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-leaf-400 focus:ring-offset-2',
        variants[variant],
        className,
      )}
      {...props}
    />
  );
});

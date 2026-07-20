import React from 'react';
import { cn } from '../../utils/cn';

type Tone = 'neutral' | 'success' | 'warning' | 'danger' | 'info';

const TONE_CLASSES: Record<Tone, string> = {
  neutral: 'bg-sunken text-text-secondary',
  success: 'bg-emerald-500/10 text-emerald-500',
  warning: 'bg-amber-500/10 text-amber-500',
  danger: 'bg-rose-500/10 text-rose-500',
  info: 'bg-blue-500/10 text-blue-500',
};

export function Badge({ tone = 'neutral', children, className }: { tone?: Tone; children: React.ReactNode; className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium', TONE_CLASSES[tone], className)}>
      {children}
    </span>
  );
}

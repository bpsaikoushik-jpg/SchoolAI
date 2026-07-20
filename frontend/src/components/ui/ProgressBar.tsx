import { cn } from '../../utils/cn';

export function ProgressBar({ value, tint = 'var(--color-brand-500)', className, height = 8 }: { value: number; tint?: string; className?: string; height?: number }) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className={cn('w-full overflow-hidden rounded-full bg-sunken', className)} style={{ height }}>
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{ width: `${clamped}%`, background: tint }}
      />
    </div>
  );
}

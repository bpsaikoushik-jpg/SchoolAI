import { cn } from '../../utils/cn';

export function Spinner({ size = 20, className }: { size?: number; className?: string }) {
  return (
    <div
      className={cn('animate-spin rounded-full border-2 border-current border-t-transparent text-brand-500', className)}
      style={{ width: size, height: size }}
      role="status"
      aria-label="Loading"
    />
  );
}

export function FullPageSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex h-full min-h-[60vh] w-full flex-col items-center justify-center gap-3 text-text-muted">
      <Spinner size={28} />
      <p className="text-sm">{label}</p>
    </div>
  );
}

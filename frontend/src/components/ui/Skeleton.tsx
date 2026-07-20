import { cn } from '../../utils/cn';

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-lg bg-sunken', className)} />;
}

export function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-border-subtle bg-raised p-6">
      <Skeleton className="h-10 w-10 rounded-xl mb-4" />
      <Skeleton className="h-3 w-24 mb-2" />
      <Skeleton className="h-6 w-16" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  );
}

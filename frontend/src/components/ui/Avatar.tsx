import { cn } from '../../utils/cn';

function initials(name?: string | null) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  return (parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? '');
}

export function Avatar({ name, size = 40, ringColor, className }: { name?: string | null; size?: number; ringColor?: string; className?: string }) {
  return (
    <div
      className={cn('grid shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand-500 to-mint-500 font-semibold text-white', className)}
      style={{
        width: size,
        height: size,
        fontSize: size * 0.38,
        boxShadow: ringColor ? `0 0 0 2px var(--surface-raised), 0 0 0 4px ${ringColor}` : undefined,
      }}
    >
      {initials(name).toUpperCase()}
    </div>
  );
}

import type { LucideIcon } from 'lucide-react';
import { Inbox } from 'lucide-react';
import { Button } from '../Button';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ icon: Icon = Inbox, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-border-strong py-14 text-center">
      <div className="grid h-12 w-12 place-items-center rounded-full bg-sunken text-text-muted">
        <Icon size={22} />
      </div>
      <div>
        <p className="font-medium text-text-primary">{title}</p>
        {description && <p className="mt-1 max-w-sm text-sm text-text-muted">{description}</p>}
      </div>
      {actionLabel && onAction && (
        <Button size="sm" variant="outline" onClick={onAction} className="mt-1">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

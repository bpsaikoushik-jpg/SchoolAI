import { AlertTriangle } from 'lucide-react';
import { Button } from '../Button';

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
}

export function ErrorState({ title = 'Something went wrong', description = 'That didn\'t load. Try again.', onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-rose-500/20 bg-rose-500/5 py-14 text-center">
      <div className="grid h-12 w-12 place-items-center rounded-full bg-rose-500/10 text-rose-500">
        <AlertTriangle size={22} />
      </div>
      <div>
        <p className="font-medium text-text-primary">{title}</p>
        <p className="mt-1 max-w-sm text-sm text-text-muted">{description}</p>
      </div>
      {onRetry && (
        <Button size="sm" variant="outline" onClick={onRetry} className="mt-1">
          Try again
        </Button>
      )}
    </div>
  );
}

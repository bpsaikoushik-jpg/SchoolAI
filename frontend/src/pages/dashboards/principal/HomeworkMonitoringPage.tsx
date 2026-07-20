import { Card, Badge, ProgressBar, FullPageSpinner, ErrorState, EmptyState } from '../../../components/ui';
import { ClipboardList } from 'lucide-react';
import { useHomeworkOverview } from '../../../hooks/usePrincipal';

const ACCENT = 'var(--color-role-principal)';

export function HomeworkMonitoringPage() {
  const { data, isLoading, isError, refetch } = useHomeworkOverview();

  const sorted = [...(data ?? [])].sort((a, b) => {
    if (!a.due_date) return 1;
    if (!b.due_date) return -1;
    return new Date(b.due_date).getTime() - new Date(a.due_date).getTime();
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Homework Monitoring</h1>
        <p className="text-sm text-text-muted">Everything assigned across the school's classes.</p>
      </div>

      {isLoading ? (
        <FullPageSpinner label="Loading homework…" />
      ) : isError ? (
        <ErrorState description="Couldn't load homework right now." onRetry={() => refetch()} />
      ) : sorted.length === 0 ? (
        <EmptyState icon={ClipboardList} title="No homework assigned yet" description="Once teachers assign homework, it will show up here." />
      ) : (
        <div className="space-y-3">
          {sorted.map((hw) => (
            <Card key={hw.id} className="flex flex-wrap items-center justify-between gap-4">
              <div className="min-w-[200px] flex-1">
                <p className="font-medium text-text-primary">{hw.title}</p>
                <p className="text-sm text-text-muted">
                  {hw.class_name} · Due {hw.due_date ? new Date(hw.due_date).toLocaleDateString() : 'No due date'}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <ProgressBar value={hw.completion_rate ?? 0} tint={ACCENT} className="w-32" />
                <span className="text-sm text-text-secondary">{hw.submitted}/{hw.total_students}</span>
                <Badge tone={(hw.completion_rate ?? 0) >= 80 ? 'success' : (hw.completion_rate ?? 0) >= 40 ? 'warning' : 'danger'}>
                  {hw.completion_rate != null ? `${hw.completion_rate}%` : '—'}
                </Badge>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

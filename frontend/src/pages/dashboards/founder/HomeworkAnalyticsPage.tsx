import { Card, CardHeader, Table, ProgressBar, FullPageSpinner, ErrorState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useOrgHomework } from '../../../hooks/useFounder';
import type { OrgHomeworkSummary } from '../../../types/founder';

const ACCENT = 'var(--color-role-founder)';

const columns: Column<OrgHomeworkSummary>[] = [
  { key: 'school_name', header: 'School' },
  { key: 'total_assigned', header: 'Assigned' },
  { key: 'total_submitted', header: 'Submitted' },
  {
    key: 'completion_rate', header: 'Completion',
    render: (r) => (
      <div className="flex items-center gap-2">
        <div className="w-28"><ProgressBar value={r.completion_rate ?? 0} tint={ACCENT} /></div>
        <span className="text-xs text-text-muted">{r.completion_rate != null ? `${r.completion_rate}%` : '—'}</span>
      </div>
    ),
  },
];

export function HomeworkAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useOrgHomework();

  if (isLoading) return <FullPageSpinner label="Loading homework analytics…" />;
  if (isError) return <ErrorState description="Couldn't load homework analytics right now." onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Homework Analytics</h1>
        <p className="text-sm text-text-muted">Organization-wide homework assignment and completion, by school.</p>
      </div>

      <Card padded={false}>
        <div className="p-4">
          <CardHeader title="By school" />
          {(data ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No homework assigned yet.</p>
          ) : (
            <Table columns={columns} data={data!} keyField="school_id" />
          )}
        </div>
      </Card>
    </div>
  );
}

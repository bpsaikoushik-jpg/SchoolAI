import { Card, Table, Badge, FullPageSpinner, ErrorState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useOrgExams } from '../../../hooks/useFounder';
import type { OrgExamSummary } from '../../../types/founder';

const columns: Column<OrgExamSummary>[] = [
  { key: 'school_name', header: 'School' },
  { key: 'total_exams', header: 'Exams held' },
  { key: 'results_recorded', header: 'Results recorded' },
  {
    key: 'average_score', header: 'Average score',
    render: (r) => <Badge tone="neutral">{r.average_score != null ? `${r.average_score}%` : '—'}</Badge>,
  },
];

export function ExamAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useOrgExams();

  if (isLoading) return <FullPageSpinner label="Loading exam analytics…" />;
  if (isError) return <ErrorState description="Couldn't load exam analytics right now." onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Exam Analytics</h1>
        <p className="text-sm text-text-muted">Organization-wide exam activity, by school.</p>
      </div>

      <Card padded={false}>
        <div className="p-4">
          {(data ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No exams recorded yet.</p>
          ) : (
            <Table columns={columns} data={data!} keyField="school_id" />
          )}
        </div>
      </Card>
    </div>
  );
}

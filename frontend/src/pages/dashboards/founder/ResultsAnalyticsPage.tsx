import { Card, Table, Badge, BarChart, CardHeader, FullPageSpinner, ErrorState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useOrgExams } from '../../../hooks/useFounder';
import type { OrgExamSummary } from '../../../types/founder';

const ACCENT = 'var(--color-role-founder)';

function scoreTone(score: number | null) {
  if (score == null) return 'neutral' as const;
  if (score >= 75) return 'success' as const;
  if (score >= 55) return 'warning' as const;
  return 'danger' as const;
}

const columns: Column<OrgExamSummary>[] = [
  { key: 'school_name', header: 'School' },
  { key: 'results_recorded', header: 'Results recorded' },
  {
    key: 'average_score', header: 'Average score',
    render: (r) => <Badge tone={scoreTone(r.average_score)}>{r.average_score != null ? `${r.average_score}%` : '—'}</Badge>,
  },
];

export function ResultsAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useOrgExams();

  if (isLoading) return <FullPageSpinner label="Loading results analytics…" />;
  if (isError) return <ErrorState description="Couldn't load results analytics right now." onRetry={() => refetch()} />;

  const chartData = (data ?? [])
    .filter((s) => s.average_score != null)
    .map((s) => ({ label: s.school_name, value: s.average_score as number }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Results Analytics</h1>
        <p className="text-sm text-text-muted">Organization-wide average results, by school.</p>
      </div>

      <Card>
        <CardHeader title="Average score by school" />
        {chartData.length === 0 ? (
          <p className="py-8 text-center text-sm text-text-muted">No graded results yet.</p>
        ) : (
          <BarChart data={chartData} tint={ACCENT} valueSuffix="%" />
        )}
      </Card>

      <Card padded={false}>
        <div className="p-4">
          {(data ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No results recorded yet.</p>
          ) : (
            <Table columns={columns} data={data!} keyField="school_id" />
          )}
        </div>
      </Card>
    </div>
  );
}

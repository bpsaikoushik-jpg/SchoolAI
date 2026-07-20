import { Card, CardHeader, Table, Badge, BarChart, FullPageSpinner, ErrorState, EmptyState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { BarChart3 } from 'lucide-react';
import { useExamsOverview } from '../../../hooks/usePrincipal';
import type { ExamOverviewItem } from '../../../types/principal';

const ACCENT = 'var(--color-role-principal)';

function scoreTone(score: number | null) {
  if (score == null) return 'neutral' as const;
  if (score >= 75) return 'success' as const;
  if (score >= 55) return 'warning' as const;
  return 'danger' as const;
}

const columns: Column<ExamOverviewItem>[] = [
  { key: 'title', header: 'Exam' },
  { key: 'subject_name', header: 'Subject' },
  { key: 'class_name', header: 'Class', render: (r) => r.class_name ?? '—' },
  { key: 'results_recorded', header: 'Results' },
  {
    key: 'average_score', header: 'Average score',
    render: (r) => <Badge tone={scoreTone(r.average_score)}>{r.average_score != null ? `${r.average_score}%` : 'Not graded'}</Badge>,
  },
];

export function ResultsMonitoringPage() {
  const { data, isLoading, isError, refetch } = useExamsOverview();

  const graded = (data ?? []).filter((e) => e.average_score != null);
  const chartData = graded
    .slice(0, 8)
    .map((e) => ({ label: e.title, value: e.average_score ?? 0 }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Results Monitoring</h1>
        <p className="text-sm text-text-muted">Average scores recorded per exam across the school.</p>
      </div>

      {isLoading ? (
        <FullPageSpinner label="Loading results…" />
      ) : isError ? (
        <ErrorState description="Couldn't load results right now." onRetry={() => refetch()} />
      ) : (data ?? []).length === 0 ? (
        <EmptyState icon={BarChart3} title="No results recorded yet" description="Once exam results are graded, they'll appear here." />
      ) : (
        <>
          {chartData.length > 0 && (
            <Card>
              <CardHeader title="Average score by exam" subtitle="Most recent 8 graded exams" />
              <BarChart data={chartData} tint={ACCENT} valueSuffix="%" />
            </Card>
          )}
          <Card padded={false}>
            <div className="p-4">
              <Table columns={columns} data={data!} keyField="id" />
            </div>
          </Card>
        </>
      )}
    </div>
  );
}

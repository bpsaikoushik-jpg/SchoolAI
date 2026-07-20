import { Card, CardHeader, Table, Badge, FullPageSpinner, ErrorState, BarChart } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useOrgStudentAnalytics } from '../../../hooks/useFounder';
import type { SchoolStudentSummary } from '../../../types/founder';

const ACCENT = 'var(--color-role-founder)';

function scoreTone(score: number | null) {
  if (score == null) return 'neutral' as const;
  if (score >= 75) return 'success' as const;
  if (score >= 55) return 'warning' as const;
  return 'danger' as const;
}

const columns: Column<SchoolStudentSummary>[] = [
  { key: 'school_name', header: 'School' },
  { key: 'student_count', header: 'Students' },
  {
    key: 'average_score', header: 'Average score',
    render: (r) => <Badge tone={scoreTone(r.average_score)}>{r.average_score != null ? `${r.average_score}%` : '—'}</Badge>,
  },
];

export function StudentAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useOrgStudentAnalytics();

  if (isLoading) return <FullPageSpinner label="Loading student analytics…" />;
  if (isError) return <ErrorState description="Couldn't load student analytics right now." onRetry={() => refetch()} />;

  const gradeChart = (data?.by_grade ?? []).map((g) => ({
    label: g.grade_level != null ? `Grade ${g.grade_level}` : 'Unspecified',
    value: g.count,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Student Analytics</h1>
        <p className="text-sm text-text-muted">Organization-wide student counts and performance, by school and grade.</p>
      </div>

      <Card>
        <CardHeader title="Students by grade level" />
        {gradeChart.length === 0 ? (
          <p className="py-8 text-center text-sm text-text-muted">No student profiles recorded yet.</p>
        ) : (
          <BarChart data={gradeChart} tint={ACCENT} />
        )}
      </Card>

      <Card padded={false}>
        <div className="p-4">
          <CardHeader title="By school" />
          {(data?.by_school ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No schools with students yet.</p>
          ) : (
            <Table columns={columns} data={data!.by_school} keyField="school_id" />
          )}
        </div>
      </Card>
    </div>
  );
}

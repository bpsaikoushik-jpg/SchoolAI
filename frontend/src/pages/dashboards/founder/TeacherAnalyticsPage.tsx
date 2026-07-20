import { Card, CardHeader, Table, Badge, FullPageSpinner, ErrorState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useOrgTeacherAnalytics } from '../../../hooks/useFounder';
import type { SchoolTeacherSummary, TopTeacher } from '../../../types/founder';

function scoreTone(score: number | null) {
  if (score == null) return 'neutral' as const;
  if (score >= 75) return 'success' as const;
  if (score >= 55) return 'warning' as const;
  return 'danger' as const;
}

const schoolColumns: Column<SchoolTeacherSummary>[] = [
  { key: 'school_name', header: 'School' },
  { key: 'teacher_count', header: 'Teachers' },
];

const topColumns: Column<TopTeacher>[] = [
  { key: 'full_name', header: 'Teacher', render: (r) => r.full_name ?? '—' },
  { key: 'school_name', header: 'School' },
  { key: 'subjects_taught', header: 'Subjects', render: (r) => r.subjects_taught.join(', ') || '—' },
  {
    key: 'average_student_score', header: 'Avg. student score',
    render: (r) => <Badge tone={scoreTone(r.average_student_score)}>{r.average_student_score != null ? `${r.average_student_score}%` : '—'}</Badge>,
  },
];

export function TeacherAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useOrgTeacherAnalytics();

  if (isLoading) return <FullPageSpinner label="Loading teacher analytics…" />;
  if (isError) return <ErrorState description="Couldn't load teacher analytics right now." onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Teacher Analytics</h1>
        <p className="text-sm text-text-muted">Organization-wide teacher counts and top performers by student outcomes.</p>
      </div>

      <Card padded={false}>
        <div className="p-4">
          <CardHeader title="Teachers by school" />
          {(data?.by_school ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No schools with teachers yet.</p>
          ) : (
            <Table columns={schoolColumns} data={data!.by_school} keyField="school_id" />
          )}
        </div>
      </Card>

      <Card padded={false}>
        <div className="p-4">
          <CardHeader title="Top teachers" subtitle="By average student score" />
          {(data?.top_teachers ?? []).length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No graded results yet.</p>
          ) : (
            <Table columns={topColumns} data={data!.top_teachers} keyField="teacher_id" />
          )}
        </div>
      </Card>
    </div>
  );
}

import { Card, CardHeader, Table, Badge, BarChart, FullPageSpinner, ErrorState, EmptyState } from '../../../components/ui';
import type { Column } from '../../../components/ui';
import { useSubjectPerformance, useTeacherPerformance } from '../../../hooks/usePrincipal';
import type { SubjectPerformance, TeacherPerformance } from '../../../types/principal';

const ACCENT = 'var(--color-role-principal)';

function scoreTone(score: number | null) {
  if (score == null) return 'neutral' as const;
  if (score >= 75) return 'success' as const;
  if (score >= 55) return 'warning' as const;
  return 'danger' as const;
}

const subjectColumns: Column<SubjectPerformance>[] = [
  { key: 'subject_name', header: 'Subject' },
  { key: 'total_exams', header: 'Exams' },
  {
    key: 'average_score', header: 'Average score',
    render: (r) => <Badge tone={scoreTone(r.average_score)}>{r.average_score != null ? `${r.average_score}%` : '—'}</Badge>,
  },
];

const teacherColumns: Column<TeacherPerformance>[] = [
  { key: 'full_name', header: 'Teacher', render: (r) => r.full_name ?? 'Unnamed teacher' },
  { key: 'subjects_taught', header: 'Subjects', render: (r) => (r.subjects_taught.length ? r.subjects_taught.join(', ') : '—') },
  {
    key: 'average_student_score', header: "Students' average score",
    render: (r) => <Badge tone={scoreTone(r.average_student_score)}>{r.average_student_score != null ? `${r.average_student_score}%` : '—'}</Badge>,
  },
];

export function TeacherAnalyticsPage() {
  const { data: subjects, isLoading: loadingSubjects, isError: errSubjects, refetch: refetchSubjects } = useSubjectPerformance();
  const { data: teachers, isLoading: loadingTeachers, isError: errTeachers, refetch: refetchTeachers } = useTeacherPerformance();

  const chartData = (subjects ?? [])
    .filter((s) => s.average_score != null)
    .map((s) => ({ label: s.subject_name, value: s.average_score as number }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Academic Analytics</h1>
        <p className="text-sm text-text-muted">Subject and faculty performance across the school.</p>
      </div>

      {loadingSubjects ? (
        <FullPageSpinner label="Loading subject performance…" />
      ) : errSubjects ? (
        <ErrorState description="Couldn't load subject performance right now." onRetry={() => refetchSubjects()} />
      ) : (
        <>
          {chartData.length > 0 && (
            <Card>
              <CardHeader title="Average score by subject" />
              <BarChart data={chartData} tint={ACCENT} valueSuffix="%" />
            </Card>
          )}
          <Card padded={false}>
            <div className="p-4">
              <CardHeader title="Subjects" />
              {(subjects ?? []).length === 0 ? (
                <EmptyState title="No subjects yet" description="Once subjects are added, their performance will appear here." />
              ) : (
                <Table columns={subjectColumns} data={subjects!} keyField="subject_id" />
              )}
            </div>
          </Card>
        </>
      )}

      {loadingTeachers ? (
        <FullPageSpinner label="Loading teacher performance…" />
      ) : errTeachers ? (
        <ErrorState description="Couldn't load teacher performance right now." onRetry={() => refetchTeachers()} />
      ) : (
        <Card padded={false}>
          <div className="p-4">
            <CardHeader title="Faculty overview" />
            {(teachers ?? []).length === 0 ? (
              <EmptyState title="No teachers yet" description="Once teachers are added, their performance will appear here." />
            ) : (
              <Table columns={teacherColumns} data={teachers!} keyField="teacher_id" />
            )}
          </div>
        </Card>
      )}
    </div>
  );
}

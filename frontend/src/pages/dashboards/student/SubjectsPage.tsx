import { Card, CardHeader, ProgressBar, Badge, Spinner, EmptyState, ErrorState } from '../../../components/ui';
import { useMySubjects } from '../../../hooks/useAcademic';
import { useExamsBySubject, useMyResults } from '../../../hooks/useExams';
import type { Subject } from '../../../types/academic';

function SubjectCard({ subject }: { subject: Subject }) {
  const { data: exams } = useExamsBySubject(subject.id);
  const { data: results } = useMyResults();

  const examIds = new Set((exams ?? []).map((e) => e.id));
  const scoredResults = (results ?? []).filter((r) => examIds.has(r.exam_id) && r.score !== null);
  const avgScore = scoredResults.length
    ? Math.round(scoredResults.reduce((sum, r) => sum + (r.score ?? 0), 0) / scoredResults.length)
    : null;

  return (
    <Card>
      <CardHeader
        title={subject.name}
        subtitle={subject.teacher_id ? 'Teacher assigned' : 'No teacher assigned yet'}
        action={
          <Badge tone={avgScore === null ? 'neutral' : avgScore >= 70 ? 'success' : 'warning'}>
            {avgScore === null ? 'No results yet' : `${avgScore}%`}
          </Badge>
        }
      />
      <p className="mb-1.5 text-xs text-text-muted">Average exam score</p>
      <ProgressBar value={avgScore ?? 0} tint="var(--color-role-student)" />
      <p className="mt-1.5 text-right text-xs font-medium text-text-secondary">
        {scoredResults.length} graded exam{scoredResults.length === 1 ? '' : 's'}
      </p>
    </Card>
  );
}

export function SubjectsPage() {
  const { data: subjects, isLoading, isError, refetch } = useMySubjects();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Subjects</h1>
        <p className="text-sm text-text-muted">Your enrolled subjects this term.</p>
      </div>
      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : isError ? (
        <ErrorState description="Couldn't load your subjects." onRetry={() => refetch()} />
      ) : !subjects || subjects.length === 0 ? (
        <EmptyState title="No subjects yet" description="You aren't enrolled in any classes with subjects yet." />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {subjects.map((s) => (
            <SubjectCard key={s.id} subject={s} />
          ))}
        </div>
      )}
    </div>
  );
}
